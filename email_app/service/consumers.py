import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'email_app.settings')

import django
django.setup()

import json

from channels.generic.websocket import AsyncWebsocketConsumer

from service.models import Message


class MessageStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.message_uuid = self.scope.get('url_route').get('kwargs').get('message_uuid')
        await self.channel_layer.group_add(self.message_uuid, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.message_uuid, self.channel_name)
        try:
            await self.send(text_data=json.dumps({
                'status': 'close',
                'code': close_code
            }))
        except RuntimeError:  # handling 'ws already closed or response already completed'
            pass

    async def receive(self, text_data):
        data_json = json.loads(text_data)
        type_data = data_json.get('type')
        status_data = data_json.get('status')
        await self.channel_layer.group_send(
            self.message_uuid,
            {
                'type': type_data,
                'status': status_data
            }
        )

    async def message_status(self, event):
        status = event.get('status')
        returned_data = {
            'type': 'message_status',
            'status': status
        }
        await self.send(json.dumps(returned_data))
        await self.disconnect(close_code=1000)

    async def check_status(self, event):
        message = await Message.objects.aget(uuid=self.message_uuid)
        returned_data = {
            'type': 'message_status',
            'status': message.status
        }
        await self.send(json.dumps(returned_data))
