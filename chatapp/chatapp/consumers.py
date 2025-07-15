import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from .models import Message
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.other_user = self.scope['url_route']['kwargs']['username']
        self.user = self.scope['user']
        self.room_group_name = f'chat_{min(self.user.username, self.other_user)}_{max(self.user.username, self.other_user)}'

        # Join chat group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender = self.user
        receiver_username = self.other_user

        # Fetch receiver user from DB
        User = get_user_model()
        receiver = await sync_to_async(User.objects.get)(username=receiver_username)

        # Save the message to DB
        await sync_to_async(Message.objects.create)(
            sender=sender,
            receiver=receiver,
            content=message
        )

        # Broadcast to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender.username,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender']
        }))
