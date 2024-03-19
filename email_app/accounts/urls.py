# from rest_framework_simplejwt.views import TokenRefreshView

from django.urls import path

from .views import (
    RegisterView,
    LoginAPIView,
    logout,
    token_refresh,
)


urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginAPIView.as_view(), name='login'),
    path('logout', logout, name='logout'),
    path('token/refresh', token_refresh, name='token_refresh'),
]
