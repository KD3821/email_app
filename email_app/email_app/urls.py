from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)

from django.contrib import admin
from django.urls import path, include

from service.views import (
    CampaignViewSet,
    CustomerViewSet,
    MessageViewSet,
    SingleCampaignReportView,
    AllCampaignsReportView,
)


router = DefaultRouter()
router.register(r'campaigns', CampaignViewSet, basename='campaigns')
router.register(r'customers', CustomerViewSet, basename='customers')
router.register(r'messages', MessageViewSet, basename='messages')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/reports/', AllCampaignsReportView.as_view(), name='all_report'),
    path('api/reports/<int:id>/', SingleCampaignReportView.as_view(), name='single_report'),
    path('api/', include(router.urls)),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
