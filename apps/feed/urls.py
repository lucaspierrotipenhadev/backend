# apps/social/urls.py
from django.urls import path
from .views import FeedView

app_name = 'social'

urlpatterns = [
    path('feed/', FeedView.as_view(), name='feed'),
]