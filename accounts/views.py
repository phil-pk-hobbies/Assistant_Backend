from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from .serializers import UserSerializer, UserCreateSerializer

User = get_user_model()

class UserAdminViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(methods=['post'], detail=True, url_path='reset_password',
            permission_classes=[IsAdminUser])
    def reset_password(self, request, pk=None):
        user = self.get_object()
        new_pwd = request.data.get('new_password') or User.objects.make_random_password()
        validate_password(new_pwd, user)
        user.set_password(new_pwd)
        user.save()
        masked = '********' if 'new_password' in request.data else new_pwd
        return Response({'new_password': masked}, status=status.HTTP_200_OK)
