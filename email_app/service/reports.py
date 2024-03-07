from dataclasses import dataclass
from datetime import datetime

from django.utils import timezone
from django.db.models import Sum, Count, Q

from accounts.models import User
from .models import Campaign


@dataclass
class SingleCampaignReport:
    date: datetime
    msg_total: int
    msg_ok: int
    msg_failed: int
    msg_canceled: int
    msg_processing: int


@dataclass
class AllCampaignsReport:
    date: datetime
    campaign_total: int
    msg_total: int
    msg_ok: int
    msg_failed: int
    msg_canceled: int
    msg_processing: int


def prepare_queryset(obj: Campaign | User):
    ok_status = Count('messages', filter=Q(messages__status='ok'))
    failed_status = Count('messages', filter=Q(messages__status='failed'))
    canceled_status = Count('messages', filter=Q(messages__status='canceled'))
    processing_status = Count('messages', filter=Q(messages__status='processing'))

    if isinstance(obj, Campaign):
        campaign_qs = Campaign.objects.filter(id=obj.pk)
    else:
        campaign_qs = Campaign.objects.filter(owner=obj)

    qs = (campaign_qs
          .annotate(ok_num=ok_status)
          .annotate(failed_num=failed_status)
          .annotate(canceled_num=canceled_status)
          .annotate(processing_num=processing_status)
          .annotate(total=Count('messages')))

    return qs


def get_single_campaign_data(campaign):
    campaign_qs = prepare_queryset(campaign)

    data = SingleCampaignReport(
        date=timezone.now(),
        msg_total=campaign_qs[0].total,
        msg_ok=campaign_qs[0].ok_num,
        msg_failed=campaign_qs[0].failed_num,
        msg_canceled=campaign_qs[0].canceled_num,
        msg_processing=campaign_qs[0].processing_num
    )
    return data


def get_all_campaigns_data(user):
    campaigns = prepare_queryset(user)

    data = AllCampaignsReport(
        date=timezone.now(),
        campaign_total=campaigns.count(),
        msg_total=campaigns.aggregate(Sum('total')).get('total__sum'),
        msg_ok=campaigns.aggregate(Sum('ok_num')).get('ok_num__sum'),
        msg_failed=campaigns.aggregate(Sum('failed_num')).get('failed_num__sum'),
        msg_canceled=campaigns.aggregate(Sum('canceled_num')).get('canceled_num__sum'),
        msg_processing=campaigns.aggregate(Sum('processing_num')).get('processing_num__sum')
    )

    return data
