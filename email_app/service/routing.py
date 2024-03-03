from django.urls import re_path

from .consumers import MessageStatusConsumer


websocket_urlpatterns = [
    re_path(r'ws/campaign/$', MessageStatusConsumer.as_asgi()),
    # re_path(r'ws/statuses/(?P<campaign_id>\d+)/$', MessageStatusConsumer.as_asgi()),
]
