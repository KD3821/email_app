import os
import urllib3
from time import sleep
import logging
import datetime

import requests
from requests.adapters import HTTPAdapter, Retry
from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.utils import timezone

from .models import Message, Campaign
from .utils import (
    create_messages,
    schedule_message,
    schedule_check_campaign,
    cancel_message_schedule,
    resume_message_schedule,
    cancel_campaign_schedule,
    cancel_campaign_check,
)


logger = logging.getLogger(__name__)

channel_layer = get_channel_layer()

api_key = os.getenv('API_KEY')
api_host = os.getenv('API_HOST')
auth = {'Authorization': f'Bearer {api_key}'}


@shared_task
def send_message(message_uuid: str, seconds_for_retry: int = 60):  # retry to send during 1 min
    now_date = timezone.now()
    msg = Message.objects.get(uuid=message_uuid)
    cancel_message_schedule(message_uuid)

    if msg.campaign.status == Campaign.CANCELED:
        msg.status = Message.CANCELED
        msg.save()
        async_to_sync(channel_layer.group_send)(
            msg.uuid,
            {
                'type': 'message_status',
                'status': 'canceled'
            }
        )
        logger.info(f'Отмена отправки сообщения [{message_uuid}] в [{now_date}] - статус рассылки "отменена".')
        return message_uuid

    elif (now_date - msg.sent_at) >= datetime.timedelta(seconds=seconds_for_retry):
        msg.status = Message.FAILED
        msg.save()
        async_to_sync(channel_layer.group_send)(
            msg.uuid,
            {
                'type': 'message_status',
                'status': 'failed'
            }
        )
        logger.info(f'Ошибка отправки сообщения [{message_uuid}] в [{now_date}] - закончилось время повторной отправки')
        return message_uuid

    elif now_date < msg.campaign.finish_at:
        msg_id = msg.pk
        phone = str(msg.customer.phone)
        text = msg.campaign.text
        msg_data = {
            'id': msg_id,
            'phone': phone,
            'text': text
        }
        sleep(5)
        s = requests.Session()
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))
        try:
            response = s.post(
                url=f'{api_host}{msg_id}',
                json=msg_data,
                headers=auth
            )
        except (urllib3.exceptions.MaxRetryError, requests.exceptions.ConnectionError):
            logger.info(
                f'Сбой HTTP соединения в [{now_date}] при отправке сообщения [{message_uuid}] - будет повторная попытка'
            )
            resume_message_schedule(message_uuid)
            return message_uuid

        if response.status_code == requests.codes.ok:
            msg.status = Message.OK
            msg.save()
            async_to_sync(channel_layer.group_send)(
                msg.uuid,
                {
                    'type': 'message_status',
                    'status': 'ok'
                }
            )
            logger.info(f'Сообщение [{message_uuid}] успешно отправлено для [{phone}]\nТекст: {text[:40]}...')
            return message_uuid

        else:
            logger.info(
                f'Сбой отправки сообщения [{message_uuid}] в [{now_date}]: код ответа != "200" - будет повторная попытка'
            )
            resume_message_schedule(message_uuid)
            return message_uuid

    elif now_date >= msg.campaign.finish_at:
        msg.status = Message.CANCELED
        msg.save()
        async_to_sync(channel_layer.group_send)(
            msg.uuid,
            {
                'type': 'message_status',
                'status': 'canceled'
            }
        )
        logger.info(f'Сообщение [{message_uuid}] отменено в [{now_date}] - наступило время завершения рассылки.')
        return message_uuid


@shared_task
def create_send_messages(campaign_id: int):
    now_date = timezone.now()
    campaign = Campaign.objects.get(id=campaign_id)

    if campaign.status == Campaign.CANCELED:
        cancel_campaign_schedule(campaign_id)
        logger.info(f'Рассылка [{campaign_id}] отменена в [{now_date}] - статус рассылки "отменена".')
        return f'Scheduled-canceled(Campaign-{campaign_id})'

    elif campaign.start_at <= now_date < campaign.finish_at:
        campaign.status = Campaign.LAUNCHED
        campaign.save()
        message_list = create_messages(campaign)
        for msg in message_list:
            schedule_message(msg.uuid)
        cancel_campaign_schedule(campaign_id)
        schedule_check_campaign(campaign_id)
        logger.info(f'Рассылка [{campaign_id}] стартовала в [{now_date}]. Кол-во сообщений: {len(message_list)}')
        return f'Scheduled-launched(Campaign-{campaign_id})'

    elif campaign.finish_at <= now_date:
        campaign.status = Campaign.FINISHED
        campaign.save()
        cancel_campaign_schedule(campaign_id)
        logger.info(f'Рассылка [{campaign_id}] завершена в [{now_date}] - наступило время завершения (без запуска).')
        return f'Scheduled-finished(Campaign-{campaign_id})'

    return f'Scheduled-checked(Campaign-{campaign_id})'


@shared_task
def check_finished_campaign(campaign_id: int):
    now_date = timezone.now()
    campaign = Campaign.objects.get(id=campaign_id)

    if campaign.finish_at <= now_date:
        campaign.status = Campaign.FINISHED
        campaign.save()
        cancel_campaign_check(campaign_id)
        logger.info(f'Рассылка [{campaign_id}] завершена в [{now_date}] - наступило время завершения.')
        return f'Finished-time(Campaign-{campaign_id})'

    elif campaign.messages.filter(status=Message.PROCESSING).count() == 0:
        campaign.status = Campaign.FINISHED
        campaign.save()
        cancel_campaign_check(campaign_id)
        logger.info(f'Рассылка [{campaign_id}] завершена в [{now_date}] - все сообщения обработаны.')
        return f'Finished-all(Campaign-{campaign_id})'
