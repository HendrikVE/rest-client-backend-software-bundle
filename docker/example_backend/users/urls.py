from rest_framework.routers import SimpleRouter

from .views import UserProfileView

router = SimpleRouter()
router.register('user-profile', UserProfileView, basename='user-profile')
urlpatterns = router.urls
