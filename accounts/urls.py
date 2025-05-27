from rest_framework.routers import DefaultRouter
from .views import UserAdminViewSet

router = DefaultRouter()
router.register('users', UserAdminViewSet, basename='user')

urlpatterns = router.urls
