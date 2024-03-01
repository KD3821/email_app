from rest_framework.viewsets import ModelViewSet

from .permissions import IsOwner
from accounts.permissions import OAuthPermission
from .serializers import (
    ReadCampaignSerializer,
    WriteCampaignSerializer,
    CustomerSerializer,
)


class CampaignViewSet(ModelViewSet):
    permission_classes = [IsOwner, OAuthPermission]

    def get_queryset(self):
        return self.request.user.campaigns.all()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadCampaignSerializer
        return WriteCampaignSerializer


class CustomerViewSet(ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [IsOwner, OAuthPermission]

    def get_queryset(self):
        return self.request.user.customers.all()
