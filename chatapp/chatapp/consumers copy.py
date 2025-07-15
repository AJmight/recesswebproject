# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from .models import User, Message
# from django.utils import timezone

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user = self.scope['user']
#         self.other_user = self.scope['url_route']['kwargs']['username']
#         self.room_name = f"chat_{min(self.user.username, self.other_user)}_{max(self.user.username, self.other_user)}"
#         self.room_group_name = f"chat_{self.room_name}"

#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         message = data['message']

#         # Save to DB
#         sender = self.user
#         receiver = await self.get_user(self.other_user)
#         await self.save_message(sender, receiver, message)

#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message,
#                 'sender': sender.username,
#             }
#         )

#     async def chat_message(self, event):
#         await self.send(text_data=json.dumps({
#             'message': event['message'],
#             'sender': event['sender'],
#         }))

#     @staticmethod
#     async def get_user(username):
#         return await User.objects.aget(username=username)

#     @staticmethod
#     async def save_message(sender, receiver, content):
#         await Message.objects.acreate(sender=sender, receiver=receiver, content=content, timestamp=timezone.now())


import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from .models import Message
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.other_user = self.scope['url_route']['kwargs']['username']
        self.room_group_name = f'chat_{min(self.scope["user"].username, self.other_user)}_{max(self.scope["user"].username, self.other_user)}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender = self.scope['user']
        receiver_username = self.scope['url_route']['kwargs']['username']

        # Get receiver user
        User = get_user_model()
        receiver = await sync_to_async(User.objects.get)(username=receiver_username)

        # Save message to database
        await sync_to_async(Message.objects.create)(
            sender=sender,
            receiver=receiver,
            content=message
        )

        # Broadcast message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender.username,
            }
        )


    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
        }))
