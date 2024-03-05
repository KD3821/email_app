from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from .permissions import IsOwner
from accounts.permissions import OAuthPermission
from .paginations import CampaignMessagesPagination
from .serializers import (
    ReadCampaignSerializer,
    WriteCampaignSerializer,
    ReadCustomerSerializer,
    WriteCustomerSerializer,
    MessageSerializer,
    CampaignMessagesSerializer,
)


class CampaignViewSet(ModelViewSet):
    permission_classes = [IsOwner]  # , OAuthPermission

    def get_queryset(self):
        return self.request.user.campaigns.order_by('id')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadCampaignSerializer
        return WriteCampaignSerializer

    @action(
        methods=['get'],
        detail=True,
        url_path='campaign-messages',
        url_name='campaign'
    )
    def get_messages(self, request, *args, **kwargs):
        campaign = self.get_object()
        messages = campaign.messages.select_related('customer').order_by('id')
        paginator = CampaignMessagesPagination()
        result_page = paginator.paginate_queryset(messages, request)
        serializer = CampaignMessagesSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class CustomerViewSet(ModelViewSet):
    permission_classes = [IsOwner]  # , OAuthPermission

    def get_queryset(self):
        return self.request.user.customers.order_by('id')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadCustomerSerializer
        return WriteCustomerSerializer


class MessageViewSet(ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return self.request.user.messages.order_by('id')
