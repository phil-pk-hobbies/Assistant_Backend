from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AssistantViewSet,
    MessageViewSet,
    ChatView,
    ResetThreadView,
    VectorStoreIdView,
    VectorStoreFilesView,
)

router = DefaultRouter()
router.register('assistants', AssistantViewSet, basename='assistant')
router.register('messages',   MessageViewSet,   basename='message')

urlpatterns = [
    path('', include(router.urls)),
    path('assistants/<uuid:pk>/chat/', ChatView.as_view(), name='chat'),
    path('assistants/<uuid:pk>/reset/', ResetThreadView.as_view(), name='reset'),
    path(
        'assistants/<uuid:pk>/vector-store/',
        VectorStoreIdView.as_view(),
        name='vector-store',
    ),
    path(
        'assistants/<uuid:pk>/vector-store/files/',
        VectorStoreFilesView.as_view(),
        name='vector-store-files',
    ),
]
