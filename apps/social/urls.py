# apps/social/urls.py
from django.urls import path
from .views import ToggleFollowView, FollowersListView, FollowingListView

app_name = 'social'

urlpatterns = [
    path('users/<int:user_id>/follow/', ToggleFollowView.as_view(), name='toggle-follow'),
    path('users/<int:user_id>/followers/', FollowersListView.as_view(), name='user-followers'),
    path('users/<int:user_id>/following/', FollowingListView.as_view(), name='user-following'),
]