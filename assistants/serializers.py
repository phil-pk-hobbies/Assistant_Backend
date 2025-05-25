from rest_framework import serializers
from .models import Assistant, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'assistant', 'role', 'content', 'created_at']
        read_only_fields = ['id', 'assistant', 'created_at']


class AssistantSerializer(serializers.ModelSerializer):
    tools = serializers.ListField(child=serializers.CharField(),
                                  required=False,  # allow it to be omitted
                                  default=list)

    messages = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Assistant
        fields = ['id', 'name', 'description', 'instructions', 'tools', 'created_at', 'messages']
        read_only_fields = ['id', 'created_at']
