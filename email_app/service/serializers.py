import logging

from rest_framework import serializers

from django.utils import timezone

from .models import Campaign, Customer

logger = logging.getLogger(__name__)


class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = [
            'phone',
            'carrier',
            'tag',
            'tz_name',
        ]


class CampaignSerializer(serializers.ModelSerializer):

    class Meta:
        model = Campaign
        fields = [
            'start_at',
            'finish_at',
            'text',
            'params'
        ]

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        finish_at = attrs.get('finish_at')
        if finish_at <= timezone.now():
            logger.info(f'Время завершения рассылки [{instance}] указано не верно: [{finish_at}]')
            raise serializers.ValidationError({
                'error': ['Время завершения рассылки не может быть в прошлом.']
            })
        return attrs
