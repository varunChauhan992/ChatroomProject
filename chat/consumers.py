# chat/consumers.py

import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .services import add_active_users, remove_active_user, get_active_user_count
from channels.db import database_sync_to_async
from .models import Room, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['slug']
        self.room_group_name = f'chat_{self.room_name}'

        # Accept connection only if user is authenticated
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Mark user active and tell everyone the new count
        await sync_to_async(add_active_users)(self.room_name, self.scope["user"].id)
        await self.broadcast_count()

    async def disconnect(self, close_code):
        # If connect() closed an anonymous user, there is nothing to clean up
        if self.scope["user"].is_anonymous:
            return

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await sync_to_async(remove_active_user)(self.room_name, self.scope["user"].id)
        await self.broadcast_count()

    async def broadcast_count(self):
        count = await sync_to_async(get_active_user_count)(self.room_name)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'active_count_update',
                'active_count': count,
            }
        )
    
    @database_sync_to_async
    def save_message(self, content):
        try:
            room = Room.objects.get(slug=self.room_name)
        except Room.DoesNotExist:
            return None
        return Message.objects.create(room=room, user=self.scope["user"], content=content)

    # Receive message from WebSocket client
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '').strip()[:1000]
        username = self.scope["user"].username

        if message:
            saved = await self.save_message(message)
            if saved is None:
                return  # room no longer exists

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                }
            )

    # Handler for 'chat_message' group event
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username'],
        }))

    # Handler for 'active_count_update' group event
    async def active_count_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'active_count_update',
            'active_count': event['active_count'],
        }))