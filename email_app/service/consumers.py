import json

from channels.generic.websocket import AsyncWebsocketConsumer


class MessageStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.message_uuid = self.scope.get('url_route').get('kwargs').get('message_uuid')
        await self.channel_layer.group_add(self.message_uuid, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.send(text_data=json.dumps({'status': f"Закрываем соединение - код: {close_code}"}))

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

    async def check_status(self, event):
        # status = event.get('status')
        returned_data = {
            'type': 'message_status',
            'status': 'ok'
        }
        await self.send(json.dumps(returned_data))
