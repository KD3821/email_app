from rest_framework.viewsets import ModelViewSet

from .permissions import IsOwner
from accounts.permissions import OAuthPermission
from .serializers import (
    CampaignSerializer,
    CustomerSerializer,
)


class CampaignViewSet(ModelViewSet):
    serializer_class = CampaignSerializer
    permission_classes = [IsOwner, OAuthPermission]

    def get_queryset(self):
        return self.request.user.campaigns.all()


class CustomerViewSet(ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [IsOwner, OAuthPermission]

    def get_queryset(self):
        return self.request.user.customers.all()
