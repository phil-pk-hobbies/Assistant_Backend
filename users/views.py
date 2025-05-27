from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveAPIView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer


class UserMeView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
