# chatapp/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from .models import Message
from asgiref.sync import sync_to_async
from django.db.models import Q

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.other_username = self.scope['url_route']['kwargs']['username']
        self.user = self.scope['user'] # The current logged-in user

        print(f"DEBUG: WebSocket connect attempt by user: {self.user.username if self.user.is_authenticated else 'Anonymous'}")
        print(f"DEBUG: Target other user: {self.other_username}")

        # --- IMPORTANT AUTHENTICATION CHECK ---
        if not self.user.is_authenticated:
            print("DEBUG: Connection denied - User is not authenticated.")
            await self.close()
            return

        # Fetch the other user object
        try:
            self.other_user = await sync_to_async(get_user_model().objects.get)(username=self.other_username)
            print(f"DEBUG: Other user found: {self.other_user.username}")
        except get_user_model().DoesNotExist:
            print(f"DEBUG: Connection denied - Other user '{self.other_username}' does not exist.")
            await self.close()
            return
        except Exception as e:
            print(f"DEBUG: Error fetching other user: {e}")
            await self.close()
            return

        # Create a unique room name for the two users (alphabetical order for consistency)
        user_usernames = sorted([self.user.username, self.other_user.username])
        self.room_group_name = f'chat_{user_usernames[0]}_{user_usernames[1]}'

        # Join chat group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"DEBUG: WebSocket connected successfully: {self.user.username} to {self.other_username} in room {self.room_group_name}")

    async def disconnect(self, close_code):
        print(f"DEBUG: WebSocket disconnected: {self.user.username if self.user.is_authenticated else 'Anonymous'} from room {getattr(self, 'room_group_name', 'N/A')} with code {close_code}")
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data['message']
        
        # Save the message to DB
        await sync_to_async(Message.objects.create)(
            sender=self.user,
            receiver=self.other_user,
            content=message_content,
            is_read=False
        )

        # Broadcast the message to the group
        # Fetch the timestamp of the newly created message for accurate display
        latest_message_timestamp = await sync_to_async(lambda: Message.objects.filter(
            sender=self.user, receiver=self.other_user, content=message_content
        ).latest('timestamp').timestamp.isoformat())()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'sender_username': self.user.username,
                'timestamp': latest_message_timestamp,
            }
        )
        print(f"DEBUG: Message received and broadcast: '{message_content}' from {self.user.username} to {self.room_group_name}")

    async def chat_message(self, event):
        message = event['message']
        sender_username = event['sender_username']
        timestamp = event['timestamp']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender_username': sender_username,
            'timestamp': timestamp,
            'is_self': sender_username == self.user.username
        }))
        print(f"DEBUG: Message sent to WebSocket: '{message}' from {sender_username}")
