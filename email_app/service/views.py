from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status

from .permissions import IsOwner
from accounts.permissions import OAuthPermission
from .models import Customer, Campaign, Message
from .paginations import CustomPagination
from .reports import get_single_campaign_data, get_all_campaigns_data
from .serializers import (
    ReadCampaignSerializer,
    WriteCampaignSerializer,
    CampaignMessagesSerializer,
    SingleCampaignReportSerializer,
    AllCampaignsReportSerializer,
    ReadCustomerSerializer,
    WriteCustomerSerializer,
    CustomerMessagesSerializer,
    MessageSerializer,
)


class CampaignViewSet(ModelViewSet):
    permission_classes = [IsOwner]  # , OAuthPermission

    def get_queryset(self):
        return self.request.user.campaigns.order_by('id')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadCampaignSerializer
        return WriteCampaignSerializer

    def destroy(self, request, *args, **kwargs):
        campaign = self.get_object()
        if campaign.messages.filter(status=Message.OK).count() != 0:
            raise serializers.ValidationError({
                'error': ['Невозможно удалить рассылку с успешно отправленными сообщениями.']
            })
        self.perform_destroy(campaign)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=True,
        url_path='campaign-messages',
        url_name='campaign'
    )
    def get_messages(self, request, *args, **kwargs):
        campaign = self.get_object()
        messages = campaign.messages.select_related('customer').order_by('id')
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(messages, request)
        serializer = CampaignMessagesSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(
        methods=['get'],
        detail=True,
        url_path='campaign-customers',
        url_name='campaign'
    )
    def get_customers(self, request, *arg, **kwargs):
        campaign = self.get_object()
        carrier = campaign.params.get('carrier')
        tag = campaign.params.get('tag')
        if tag is not None:
            customers = Customer.objects.filter(carrier=carrier, tag=tag).order_by('id')
        else:
            customers = Customer.objects.filter(carrier=carrier).order_by('id')
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(customers, request)
        serializer = ReadCustomerSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class CustomerViewSet(ModelViewSet):
    permission_classes = [IsOwner]  # , OAuthPermission

    def get_queryset(self):
        return self.request.user.customers.order_by('id')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadCustomerSerializer
        return WriteCustomerSerializer

    @action(
        methods=['get'],
        detail=True,
        url_path='customer-messages',
        url_name='customer'
    )
    def get_messages(self, request, *args, **kwargs):
        customer = self.get_object()
        messages = customer.messages.select_related('campaign').order_by('id')
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(messages, request)
        serializer = CustomerMessagesSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class MessageViewSet(ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return self.request.user.messages.order_by('id')


class SingleCampaignReportView(APIView):

    def get(self, request, *args, **kwargs):
        campaign_id = kwargs.get('id')
        try:
            campaign = Campaign.objects.filter(owner=request.user, id=campaign_id)[0:1].get()
        except Campaign.DoesNotExist:
            raise serializers.ValidationError({'error': ['Рассылка не найдена.']})
        report_data = get_single_campaign_data(campaign)
        serializer = SingleCampaignReportSerializer(instance=report_data)
        return Response(serializer.data)


class AllCampaignsReportView(APIView):

    def get(self, request, *args, **kwargs):
        report_data = get_all_campaigns_data(request.user)
        serializer = AllCampaignsReportSerializer(instance=report_data)
        return Response(serializer.data)
