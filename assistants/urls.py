from django.urls import path, include
from rest_framework.routers import DefaultRouter
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

user_share_list = AssistantUserShareViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
user_share_detail = AssistantUserShareViewSet.as_view({
    'delete': 'destroy',
})

dept_share_list = AssistantDeptShareViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
dept_share_detail = AssistantDeptShareViewSet.as_view({
    'delete': 'destroy',
})

urlpatterns = [
    path('', include(router.urls)),
    path('assistants/<uuid:assistant_pk>/shares/users/', user_share_list, name='assistant-user-share-list'),
    path('assistants/<uuid:assistant_pk>/shares/users/<int:pk>/', user_share_detail, name='assistant-user-share-detail'),
    path('assistants/<uuid:assistant_pk>/shares/departments/', dept_share_list, name='assistant-dept-share-list'),
    path('assistants/<uuid:assistant_pk>/shares/departments/<int:pk>/', dept_share_detail, name='assistant-dept-share-detail'),
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

