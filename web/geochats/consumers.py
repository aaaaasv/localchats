import json

from django.contrib.gis.geos import Point
from django.core.serializers.json import DjangoJSONEncoder
from asgiref.sync import sync_to_async

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import Message, Chat, Username
from geochats.services import (
    get_or_create_chat,
    get_or_create_user
)
from accounts.models import AnonymousUser


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.isUserPersistent = False

        user_id = await self.get_from_session('user_id')
        self.user_persistence, self.user = await get_or_create_user(user_id)

        await self.get_or_set_default_username()

        self.room_name = None
        self.room_group_name = None

        await self.accept()
        await self.send_start_user_info()

    @database_sync_to_async
    def get_from_session(self, item):
        session_item = self.scope['session'].get(item)
        return session_item

    async def disconnect(self, close_code):
        await self.remove_not_persistent_user(self.user.id)
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except AttributeError:
            pass

    @database_sync_to_async
    def get_or_set_default_username(self):
        self.username = AnonymousUser.objects.get(id=self.scope['session']['user_id']).username_set.all().last()
        if self.username is None:
            self.username = Username.objects.create(username=f'user#{self.user.id}', user=self.user)

    async def send_start_user_info(self):
        user = {
            'username': self.username.username,
            'id': self.user.id
        }
        await self.send(text_data=json.dumps({
            'user': user
        }))

    async def set_custom_username(self, username):
        self.isUserPersistent = True
        self.username = username
        await self.update_username()
        await self.send_start_user_info()

    # Receive message from WebSocket
    async def receive(self, text_data):
        # new message written

        text_data_json = json.loads(text_data)
        location = text_data_json.get('location')
        username = text_data_json.get('username')
        if username:
            await self.set_custom_username(username)
        if location:
            old_room_id = text_data_json.get('old_room_id')
            location = Point(location['lng'], location['lat'])
            await self.set_or_update_chat(location, old_room_id)

        message = text_data_json.get('message')
        if message:
            message_db = await self.save_message(message)
            # Send message to room group
            message = {
                'text': message,
                'username': message_db.username.username,
                'date': json.dumps(message_db.date.strftime("%I:%M %p"), cls=DjangoJSONEncoder),
                'user_id': message_db.username.user_id
            }
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        # message to broadcast to all users in the group
        message = event['message']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
        }))

    async def set_or_update_chat(self, location, old_room_id):
        self.room_name = await self.get_nearest_chat(location)
        try:
            old_room_group_name = self.room_group_name
        except AttributeError:
            old_room_group_name = None
        self.room_group_name = f'chat_{self.room_name}'

        if old_room_group_name != self.room_group_name:
            if old_room_group_name:
                await self.channel_layer.group_discard(
                    old_room_group_name,
                    self.channel_name
                )
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            try:
                old_room_id = int(old_room_id)
            except (TypeError, ValueError):
                old_room_id = None

            if old_room_id != self.room_name:
                # if user connects the first time
                messages = await self.get_old_messages()
                await self.send(text_data=json.dumps({
                    'old_messages': messages,
                    'room_id': self.room_name
                }))

    @database_sync_to_async
    def update_username(self):
        self.user = AnonymousUser.objects.get(id=self.user.id)
        self.username = Username.objects.create(user=self.user, username=self.username)

    @database_sync_to_async
    def get_old_messages(self):
        queryset = Chat.objects.get(id=self.room_name).message_set.all().order_by('date').values('text', 'date',
                                                                                                 'username__username',
                                                                                                 'username__user__id')
        serialized_q = json.dumps(list(queryset), cls=DjangoJSONEncoder)
        return serialized_q

    @database_sync_to_async
    def save_message(self, message):
        chat = Chat.objects.get(id=self.room_name)
        message = Message.objects.create(text=message, chat=chat, username=self.username)
        return message

    @database_sync_to_async
    def get_nearest_chat(self, user_location):
        chat = get_or_create_chat(user_location)
        return chat.id

    @database_sync_to_async
    def remove_not_persistent_user(self, user_id):
        if not self.user_persistence:
            return AnonymousUser.objects.get(id=user_id).delete()
