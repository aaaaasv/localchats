from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.db.models.signals import post_save

from accounts.models import User, Username


class Chat(models.Model):
    location = models.PointField(geography=True, default=Point(0.0, 0.0))


class Message(models.Model):
    text = models.CharField(max_length=500)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)


class AnonMessage(models.Model):
    username = models.ForeignKey(Username, on_delete=models.SET_NULL, null=True)
    message = models.OneToOneField(Message, on_delete=models.CASCADE)

    def get_username(self):
        try:
            return self.username.username
        except AttributeError:
            return "user"

    def get_user_id(self):
        try:
            return self.username.user_id
        except (User.DoesNotExist, AttributeError):
            return None


class AuthMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.OneToOneField(Message, on_delete=models.CASCADE)

    def get_username(self):
        return self.user.username

    def get_user_id(self):
        return self.user_id
