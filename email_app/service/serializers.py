from rest_framework import serializers

from django.utils import timezone

from .models import Campaign, Customer, Message, Invoice


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
            raise serializers.ValidationError({
                'error': ['Номер телефона должен содержать 11 символов.']
            })
        return attrs

    def create(self, validated_data):
        owner = self.context.get('request').user
        phone = validated_data.get('phone')
        if Customer.objects.filter(phone=phone, owner=owner).count() != 0:
            raise serializers.ValidationError({
                'error': ['Клиент с таким номером телефона уже существует']
            })
        return Customer.objects.create(**validated_data, owner=owner)

    def update(self, instance, validated_data):
        owner = self.context.get('request').user
        phone = validated_data.get('phone', instance.phone)
        if phone != instance.phone and Customer.objects.filter(phone=phone, owner=owner).count() != 0:
            raise serializers.ValidationError({
                'error': ['Клиент с таким номером телефона уже существует']
            })
        instance.phone = phone
        instance.carrier = validated_data.get('carrier', instance.carrier)
        instance.tag = validated_data.get('tag', instance.tag)
        instance.tz_name = validated_data.get('tz_name', instance.tz_name)
        instance.save()
        return instance


class ReadCampaignSerializer(serializers.ModelSerializer):
    invoice_data = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            'id',
            'confirmed_at',
            'paid_at',
            'start_at',
            'finish_at',
            'text',
            'params',
            'status',
            'invoice_data'
        ]

    def get_invoice_data(self, obj):
        try:
            invoice = obj.invoices.filter(campaign=obj, status=Invoice.PAID)[0:1].get()
        except Invoice.DoesNotExist:
            invoice = obj.invoices.filter(status=Invoice.PROCESSING).first()
        if invoice is not None:
            return {
                'invoice_number': invoice.invoice_number,
                'invoice_status': invoice.status
            }
        return None


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
            raise serializers.ValidationError({
                'error': [f'Время завершения рассылки не может быть в прошлом: {finish_at}']
            })
        if instance is not None and instance.status != Campaign.SCHEDULED:
            raise serializers.ValidationError({
                'error': ['Изменение данных невозможно - рассылка уже запущена, завершена или отменена']
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


class CustomerMessagesSerializer(serializers.ModelSerializer):
    campaign = ReadCampaignSerializer()

    class Meta:
        model = Message
        fields = [
            'id',
            'campaign',
            'sent_at',
            'status',
            'uuid'
        ]


class SingleCampaignReportSerializer(serializers.Serializer):  # noqa
    date = serializers.DateTimeField()
    msg_total = serializers.IntegerField()
    msg_ok = serializers.IntegerField()
    msg_failed = serializers.IntegerField()
    msg_canceled = serializers.IntegerField()
    msg_processing = serializers.IntegerField()


class AllCampaignsReportSerializer(serializers.Serializer):  # noqa
    date = serializers.DateTimeField()
    campaign_total = serializers.IntegerField()
    msg_total = serializers.IntegerField()
    msg_ok = serializers.IntegerField()
    msg_failed = serializers.IntegerField()
    msg_canceled = serializers.IntegerField()
    msg_processing = serializers.IntegerField()
