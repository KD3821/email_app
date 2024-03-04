from asgiref.sync import async_to_sync

from channels.layers import get_channel_layer


channel_layer = get_channel_layer()

async_to_sync(channel_layer.group_send)(
    'MSG-jYpGp6P4vuY5HxBzYkrMkc-3',
    {
        'type': 'message_status',
        'status': 'ok'
    }
)
