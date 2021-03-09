import json
import time

from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers

from asgiref.sync import sync_to_async

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import Message, Chat, AnonymousUser
from geochats.services import (
    get_or_create_chat
)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.isUserPersistent = False
        user_persistence, self.user = await self.get_or_create_user()
        if user_persistence:
            self.username = self.user.username
        else:
            self.username = f'{self.user.username}#{self.user.id}'

        self.room_name = None
        self.room_group_name = None

        await self.accept()
        await self.send_user_info()

    async def disconnect(self, close_code):
        await self.remove_user(self.user.id)
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except AttributeError:
            pass

    @sync_to_async
    def get_room_id(self):
        return self.scope['session']['room_id']

    async def send_user_info(self):
        user = {
            'username': self.username,
            'id': self.user.id
        }
        await self.send(text_data=json.dumps({
            'user': user
        }))

    async def set_custom_username(self, username):
        self.isUserPersistent = True
        self.username = username
        await self.update_username()
        await self.send_user_info()

    # Receive message from WebSocket
    async def receive(self, text_data):
        # new message written

        text_data_json = json.loads(text_data)
        location = text_data_json.get('location')
        old_room_id = text_data_json.get('old_room_id')
        username = text_data_json.get('username')
        if username:
            await self.set_custom_username(username)
        if location:
            self.scope['session']['lat'] = location['lat']
            self.scope['session']['lng'] = location['lng']
            location = Point(location['lng'], location['lat'])
            self.room_name = await self.get_nearest_chat(location)
            try:
                old_room_group_name = self.room_group_name
            except AttributeError:
                old_room_group_name = None
            self.room_group_name = f'chat_{self.room_name}'
            print(old_room_group_name, self.room_group_name)
            if old_room_group_name != self.room_group_name:
                print("CHANGING/SETTING ROOM NAME")
                if old_room_group_name:
                    await self.channel_layer.group_discard(
                        old_room_group_name,
                        self.channel_name
                    )
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )

                # TODO: Prevent double old messages sending on connection_lost-reconnection
                try:
                    old_room_id = int(old_room_id)
                except (TypeError, ValueError):
                    old_room_id = None
                if old_room_id != self.room_name:
                    messages = await self.get_old_messages()
                    await self.send(text_data=json.dumps({
                        'old_messages': messages,
                        'room_id': self.room_name
                    }))

        message = text_data_json.get('message')
        if message:
            message_db = await self.save_message(message)
            # Send message to room group
            message = {'text': message,
                       'user': self.username,
                       'date': json.dumps(message_db.date.strftime("%I:%M %p"), cls=DjangoJSONEncoder)}
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

    @database_sync_to_async
    def update_username(self):

        self.scope['session']['user_id'] = self.user.id
        self.scope['session'].save()

        user = AnonymousUser.objects.get(id=self.user.id)
        user.username = self.username
        print("NEW USERNAME", self.username)
        user.save()

    @database_sync_to_async
    def get_old_messages(self):
        queryset = Chat.objects.get(id=self.room_name).message_set.all().order_by('date').values('text', 'date',
                                                                                                 'user__username')
        serialized_q = json.dumps(list(queryset), cls=DjangoJSONEncoder)
        return serialized_q

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
    def get_or_create_user(self):
        try:
            user = AnonymousUser.objects.get(id=self.scope['session']['user_id'])
            self.scope['session']['user_id'] = user.id
            print("USER SUCCESSFULLY FOUND")
            user_persistence = True
        except (KeyError, TypeError, AnonymousUser.DoesNotExist):
            user = AnonymousUser.objects.create()
            self.user = user
            self.scope['session']['user_id'] = user.id
            self.scope['session']['user_persistence'] = False
            user_persistence = False
            print("CREATING USER", self.scope['session']['user_id'])
        self.scope['session'].save()
        return user_persistence, user

    @database_sync_to_async
    def remove_user(self, id):
        if self.scope['session']['user_persistence']:
            return
        print("DELETING USER")
        return AnonymousUser.objects.get(id=id).delete()
