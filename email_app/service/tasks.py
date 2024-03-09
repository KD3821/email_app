import os
import urllib3
from time import sleep
import logging

import requests
from requests.adapters import HTTPAdapter, Retry
from celery import shared_task
from django_celery_beat.models import PeriodicTask
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.utils import timezone

from .models import Message, Campaign
from .utils import create_messages


logger = logging.getLogger(__name__)

channel_layer = get_channel_layer()

api_key = os.getenv('API_KEY')
api_host = os.getenv('API_HOST')
auth = {'Authorization': f'Bearer {api_key}'}


@shared_task
def send_message(message_uuid):
    msg = Message.objects.filter(uuid=message_uuid).select_related('customer', 'campaign').first()
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
        response = requests.models.Response()
        response.status_code = 500
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
        logger.info(f'Сообщение [{message_uuid}] успешно отправлено для [{phone}]\nТекст сообщения: {text[:40]}...')
    return message_uuid


@shared_task
def create_send_messages(campaign_id: int):
    campaign = Campaign.objects.get(id=campaign_id)
    now_date = timezone.now()
    if campaign.start_at > now_date:
        campaign.status = Campaign.LAUNCHED
        campaign.save()
        message_list = create_messages(campaign)
        for msg in message_list:
            send_message.delay(msg.uuid)
        logger.info(f'Рассылка [{campaign_id}] стартовала в [{now_date}]. Кол-во сообщений: {len(message_list)}')
        periodic_task = PeriodicTask.objects.get(name=f'{campaign_id}-CMPGN')
        periodic_task.enabled = False
        periodic_task.save()
        logger.info(f'Периодическая задача [{periodic_task.name}] для рассылки [{campaign_id}] отменена.')
        return f'Scheduled-launch(Campaign-{campaign.pk})'
    return f'Scheduled-check(Campaign-{campaign.pk})'
