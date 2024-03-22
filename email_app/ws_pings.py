"""
for dev purpose - to check websocket connections
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'email_app.settings')

import django
django.setup()

from time import sleep

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


channel_layer = get_channel_layer()

async_to_sync(channel_layer.group_send)(
    'MSG-jYpGp6P4vuY5HxBzYkrMkc-3',
    {
        'type': 'message_status',
        'status': 'processing'
    }
)

sleep(2)

async_to_sync(channel_layer.group_send)(
    'MSG-Y6KChnq93LLi9EKh2VXati-1',
    {
        'type': 'message_status',
        'status': 'failed'
    }
)

sleep(3)

async_to_sync(channel_layer.group_send)(
    'MSG-aTUsSaWS6EEHLYQV5Rz3RN-2',
    {
        'type': 'message_status',
        'status': 'canceled'
    }
)

sleep(1)

async_to_sync(channel_layer.group_send)(
    'MSG-8GTyYD9drtRvNCBFBu5gUG-4',
    {
        'type': 'message_status',
        'status': 'ok'
    }
)
