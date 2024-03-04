from django.urls import path

from .consumers import MessageStatusConsumer


websocket_urlpatterns = [
    path('ws/messages/<str:message_uuid>/', MessageStatusConsumer.as_asgi()),
]
