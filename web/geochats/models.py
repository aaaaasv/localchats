from django.contrib.gis.db import models
from django.contrib.gis.geos import Point

from accounts.models import Username


class Chat(models.Model):
    location = models.PointField(geography=True, default=Point(0.0, 0.0))


class Message(models.Model):
    text = models.CharField(max_length=500)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    username = models.ForeignKey(Username, on_delete=models.SET_NULL, null=True)
