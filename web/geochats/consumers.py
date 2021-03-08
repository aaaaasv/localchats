import json

from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.serializers.json import DjangoJSONEncoder
from asgiref.sync import sync_to_async

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import Message, Chat, AnonymousUser
from geochats.services import (
    get_or_create_chat
)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = await self.get_room_id()
        self.room_group_name = f'chat_{self.room_name}'
        self.user = await self.get_user()

        self.username = f'{self.user.username}#{self.user.id}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.remove_user(self.user.id)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @sync_to_async
    def get_room_id(self):
        return self.scope['session']['room_id']

    # Receive message from WebSocket
    async def receive(self, text_data):
        # new message written
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        if message:
            message_db = await self.save_message(message)
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user': self.username,
                    'date': json.dumps(message_db.date.strftime("%I:%M %p"), cls=DjangoJSONEncoder)
                }
            )
        location = text_data_json.get('location')
        if location:
            location = Point(location['lng'], location['lat'])
            self.room_name = await self.get_nearest_chat(location)
            old_room_group_name = self.room_group_name
            self.room_group_name = f'chat_{self.room_name}'
            if old_room_group_name != self.room_group_name:
                print("CHANGING ROOM NAME")
                await self.channel_layer.group_discard(
                    old_room_group_name,
                    self.channel_name
                )
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
        #
        #     await self.send(text_data=json.dumps({
        #
        #     }))

    # Receive message from room group
    async def chat_message(self, event):
        # message to broadcast to all users in the group
        message = event['message']
        user = event['user']
        date = event['date']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': user,
            'date': date[1:-1]

        }))

    @database_sync_to_async
    def get_old_messages(self):
        return Chat.objects.get(id=self.room_name).message_set.all()

    @database_sync_to_async
    def save_message(self, message):
        chat = Chat.objects.get(id=self.room_name)
        message = Message.objects.create(text=message, chat=chat, user=self.user)
        return message

    @database_sync_to_async
    def get_nearest_chat(self, user_location):
        chat = get_or_create_chat(user_location)
        return chat.id

    @database_sync_to_async
    def get_user(self):
        user = AnonymousUser.objects.get(id=self.scope['session']['user_id'])
        return user

    @database_sync_to_async
    def remove_user(self, id):
        try:
            del self.scope['session']['user']
        except KeyError:
            pass
        return AnonymousUser.objects.get(id=id).delete()
