import logging

from rest_framework import serializers

from django.utils import timezone

from .models import Campaign, Customer, Message

logger = logging.getLogger(__name__)


class ReadCustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = [
            'id',
            'phone',
            'carrier',
            'tag',
            'tz_name',
        ]

class WriteCustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = [
            'phone',
            'carrier',
            'tag',
            'tz_name'
        ]

    def validate(self, attrs):
        phone = str(attrs.get('phone'))
        if len(phone) != 11:
            raise serializers.ValidationError({'error': ['Номер телефона должен содержать 11 символов.']})
        return attrs

    def create(self, validated_data):
        validated_data['owner'] = self.context.get('request').user
        return Customer.objects.create(**validated_data)


class ReadCampaignSerializer(serializers.ModelSerializer):

    class Meta:
        model = Campaign
        fields = [
            'id',
            'start_at',
            'finish_at',
            'text',
            'params',
            'status'
        ]


class WriteCampaignSerializer(serializers.ModelSerializer):

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
                'error': [f'Время завершения рассылки не может быть в прошлом: {finish_at}']
            })
        return attrs

    def create(self, validated_data):
        date = timezone.now()
        validated_data['owner'] = self.context.get('request').user
        if date < validated_data.get('start_at'):
            validated_data['status'] = Campaign.SCHEDULED
        return Campaign.objects.create(**validated_data)


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = [
            'id',
            'campaign',
            'customer',
            'sent_at',
            'status'
        ]


class CampaignMessagesSerializer(serializers.ModelSerializer):
    customer = ReadCustomerSerializer()

    class Meta:
        model = Message
        fields = [
            'id',
            'customer',
            'sent_at',
            'status',
            'uuid'
        ]
