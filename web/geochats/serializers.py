from rest_framework import serializers
from .models import AnonMessage, AuthMessage


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthMessage
        fields = ('text', 'chat', 'date', 'username')
