from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    def serialize_to_json(messages):
        message_num = 1
        user_all_messages = {}
        for message in messages:
            form = {
                'sender': message.sender.username,
                'receiver': message.receiver.username,
                'subject': message.subject,
                'content': message.content,
                'creation date': message.creation_date,
            }
            user_all_messages[message_num] = form
            message_num += 1
        return user_all_messages