# interactions/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommentViewSet, PostLikeView

router = DefaultRouter()
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    path('posts/<int:post_id>/like/', PostLikeView.as_view({'post': 'create'}), name='post-like'),
]