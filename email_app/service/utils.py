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
        campaign_customers.filter(tag=tag_filter)
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


def schedule_campaign(campaign_id: int):
    interval, _ = IntervalSchedule.objects.get_or_create(
        every=30,
        period=IntervalSchedule.SECONDS
    )
    PeriodicTask.objects.create(
        interval=interval,
        name=f'{campaign_id}-CMPGN',
        task='service.tasks.create_send_messages',
        args=json.dumps([campaign_id])
    )
