import json
from channels.generic.websocket import AsyncWebsocketConsumer


class MessageStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        status_data_json = json.loads(text_data)
        status = status_data_json.get('status')
        await self.send(text_data=json.dumps({'status': status}))
