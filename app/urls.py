from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (UserViewSet, UserProfileViewSet, CourseViewSet, LessonViewSet, VideoViewSet, CommentViewSet,
                    LikeVideoViewSet, DislikeVideoViewSet, FollowViewSet, UserRegistrationAPIView,
                    SendNotificationAPIView, SearchView)

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('userprofiles', UserProfileViewSet)
router.register('courses', CourseViewSet)
router.register('lessons', LessonViewSet)
router.register('videos', VideoViewSet)
router.register('comments', CommentViewSet)
router.register('likevideos', LikeVideoViewSet)
router.register('dislikevideos', DislikeVideoViewSet)
router.register('follows', FollowViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationAPIView.as_view(), name='register'),
    path('auth', include('rest_framework.urls')),
    path('send_notification/', SendNotificationAPIView.as_view(), name="send_notification"),
    path('search/', SearchView.as_view(), name='search'),
]