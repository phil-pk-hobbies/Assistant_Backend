from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssistantViewSet, MessageViewSet, ChatView, ChatHistoryView

router = DefaultRouter()
router.register('assistants', AssistantViewSet, basename='assistant')
router.register('messages',   MessageViewSet,   basename='message')

urlpatterns = [
    path('', include(router.urls)),
    path('assistants/<uuid:pk>/chat/', ChatView.as_view(), name='chat'),
    path('assistants/<uuid:pk>/history/', ChatHistoryView.as_view(), name='chat-history'),
]
