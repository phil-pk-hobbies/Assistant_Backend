from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from org.models import Department

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'department',
            'is_active',
            'is_staff',
        ]
        read_only_fields = ['is_staff']

class UserCreateSerializer(serializers.ModelSerializer):
    initial_password = serializers.CharField(write_only=True)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'initial_password',
            'first_name',
            'last_name',
            'department',
            'is_active',
            'is_staff',
        ]
        read_only_fields = ['is_staff']

    def create(self, validated_data):
        pwd = validated_data.pop('initial_password')
        user = User(**validated_data)
        validate_password(pwd, user)
        user.set_password(pwd)
        user.save()
        return user
