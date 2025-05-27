from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import (
    AssistantViewSet,
    MessageViewSet,
    ChatView,
    ResetThreadView,
    VectorStoreIdView,
    VectorStoreFilesView,
    VectorStoreFileView,
    AssistantUserShareViewSet,
    AssistantDeptShareViewSet,
)

router = DefaultRouter()
router.register('assistants', AssistantViewSet, basename='assistant')
router.register('messages',   MessageViewSet,   basename='message')

assistant_router = routers.NestedDefaultRouter(router, 'assistants', lookup='assistant')
assistant_router.register('shares/users', AssistantUserShareViewSet, basename='assistant-user-share')
assistant_router.register('shares/departments', AssistantDeptShareViewSet, basename='assistant-dept-share')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(assistant_router.urls)),
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
    path(
        'assistants/<uuid:pk>/vector-store/files/<str:file_id>/',
        VectorStoreFileView.as_view(),
        name='vector-store-file',
    ),
]
