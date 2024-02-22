from rest_framework.viewsets import ModelViewSet

from .models import Campaign
from .serializers import CampaignSerializer
from accounts.permissions import OAuthPermission


class CampaignViewSet(ModelViewSet):
    serializer_class = CampaignSerializer
    permission_classes = [OAuthPermission]

    def get_queryset(self):
        return Campaign.objects.all()
