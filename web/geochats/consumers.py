import json

from django.conf import settings
from django.contrib.gis.geos import Point
from asgiref.sync import sync_to_async

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import Message, PointCenter
from geochats.services import (
    get_or_create_chat
)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_location_point = await self.get_current_user_location()
        self.room_name = await self.get_nearest_chat(user_location_point)
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    @sync_to_async
    def get_current_user_location(self):
        lat = float(self.scope['session']['lat'])
        lng = float(self.scope['session']['lng'])
        point = Point(lng, lat)
        return point

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        # new message written
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        await self.save_message(message)
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        # message to broadcast to all users in the group
        message = event['message']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def save_message(self, message):
        chat = PointCenter.objects.get(id=self.room_name)
        Message.objects.create(text=message, chat=chat)


    @database_sync_to_async
    def get_nearest_chat(self, user_location):
        radius = settings.CHAT_IN_RADIUS
        chat = get_or_create_chat(radius, user_location)
        return chat.id
