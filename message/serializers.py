from message.models import Message
from rest_framework import serializers


class MessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'subject', 'content', 'creation_date']