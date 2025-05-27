from rest_framework import serializers
from .models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(trim_whitespace=True)

    class Meta:
        model = Department
        fields = ['id', 'name']
