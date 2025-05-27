from rest_framework import serializers
from .models import (
    Assistant,
    Message,
    AssistantUserAccess,
    AssistantDepartmentAccess,
    ALLOWED_MODELS,
    REASONING_EFFORT_CHOICES,
)


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
    reasoning_effort = serializers.ChoiceField(
        choices=[c[0] for c in REASONING_EFFORT_CHOICES],
        default="medium",
        required=False,
    )

    owner = serializers.SerializerMethodField()
    permission = serializers.SerializerMethodField()
    messages = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Assistant
        fields = ['id', 'name', 'description', 'instructions', 'model', 'reasoning_effort', 'tools', 'created_at', 'owner', 'permission', 'messages']
        read_only_fields = ['id', 'created_at']

    def validate_tools(self, value):
        """Filter placeholders and ensure only supported tools are used."""
        allowed = {"file_search"}

        cleaned = [t for t in value if t not in ("", "[]", "null", "undefined")]

        unknown = [t for t in cleaned if t not in allowed]
        if unknown:
            raise serializers.ValidationError(
                f"Only 'file_search' tool is supported (got: {', '.join(unknown)})"
            )

        return cleaned

    def get_owner(self, obj):
        request = self.context.get("request")
        if not request or not request.user:
            return False
        return obj.owner_id == request.user.id

    def get_permission(self, obj):
        request = self.context.get("request")
        if not request or not request.user:
            return None
        return obj.permission_for(request.user)


class AssistantShareUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantUserAccess
        fields = ("user", "permission")


class AssistantShareDeptSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantDepartmentAccess
        fields = ("department", "permission")
