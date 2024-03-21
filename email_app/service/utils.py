import json
from typing import List

from django_celery_beat.models import PeriodicTask, IntervalSchedule

from django.utils import timezone

from .models import Campaign, Customer, Message


def create_messages(campaign: Campaign) -> List[Message]:
    messages = list()
    owner = campaign.owner
    carrier_filter = campaign.params.get('carrier')
    tag_filter = campaign.params.get('tag')
    campaign_customers = Customer.objects.filter(owner=owner, carrier=carrier_filter)
    if tag_filter is not None:
        campaign_customers = campaign_customers.filter(tag=tag_filter)
    now_date = timezone.now()
    for customer in campaign_customers:
        new_message = Message.objects.create(
            owner=owner,
            campaign=campaign,
            customer=customer,
            sent_at=now_date,
            status=Message.PROCESSING,
            uuid=None
        )
        new_message.assign_uuid()
        messages.append(new_message)
    return messages


def schedule_check_campaign(campaign_id: int):
    interval = IntervalSchedule.objects.get(  # TODO now need to create Interval before running server
        every=10,
        period=IntervalSchedule.SECONDS
    )
    PeriodicTask.objects.create(
        interval=interval,
        name=f'{campaign_id}-CMPGN-CHECK',
        task='service.tasks.check_finished_campaign',
        args=json.dumps([campaign_id])
    )


def schedule_campaign(campaign_id: int):
    interval = IntervalSchedule.objects.get(  # TODO now need to create Interval before running server
        every=30,
        period=IntervalSchedule.SECONDS
    )
    PeriodicTask.objects.create(
        interval=interval,
        name=f'{campaign_id}-CMPGN',
        task='service.tasks.create_send_messages',
        args=json.dumps([campaign_id])
    )


def schedule_message(message_uuid: str):
    interval = IntervalSchedule.objects.get(  # TODO now need to create Interval before running server
        every=5,
        period=IntervalSchedule.SECONDS
    )
    PeriodicTask.objects.create(
        interval=interval,
        name=message_uuid,
        task='service.tasks.send_message',
        args=json.dumps([message_uuid])
    )


def cancel_message_schedule(message_uuid: str):
    periodic_task = PeriodicTask.objects.get(name=message_uuid)
    periodic_task.enabled = False
    periodic_task.save()


def resume_message_schedule(message_uuid: str):
    periodic_task = PeriodicTask.objects.get(name=message_uuid)
    periodic_task.enabled = True
    periodic_task.save()


def cancel_campaign_schedule(campaign_id: int):
    periodic_task = PeriodicTask.objects.get(name=f'{campaign_id}-CMPGN')
    periodic_task.enabled = False
    periodic_task.save()


def cancel_campaign_check(campaign_id: int):
    periodic_task = PeriodicTask.objects.get(name=f'{campaign_id}-CMPGN-CHECK')
    periodic_task.enabled = False
    periodic_task.save()
