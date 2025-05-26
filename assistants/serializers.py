from rest_framework import serializers
from .models import Assistant, Message, ALLOWED_MODELS


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'assistant', 'role', 'content', 'created_at']
        read_only_fields = ['id', 'assistant', 'created_at']


class AssistantSerializer(serializers.ModelSerializer):
    tools = serializers.ListField(
        child=serializers.CharField(),
        required=False,  # allow it to be omitted
        default=list,
    )
    model = serializers.ChoiceField(choices=ALLOWED_MODELS, default="gpt-4o")

    messages = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Assistant
        fields = ['id', 'name', 'description', 'instructions', 'model', 'tools', 'created_at', 'messages']
        read_only_fields = ['id', 'created_at']

    def validate_tools(self, value):
        """Only allow the optional ``file_search`` tool."""
        allowed = {"file_search"}
        unknown = [t for t in value if t not in allowed]
        if unknown:
            raise serializers.ValidationError(
                f"Only 'file_search' tool is supported (got: {', '.join(unknown)})"
            )
        return value
