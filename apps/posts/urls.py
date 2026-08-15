from django.urls import path
from .views import PostListCreateView, PostDetailView

app_name = 'posts'

urlpatterns = [
    path('', PostListCreateView.as_view(), name='post_list_create'),
    path('<int:pk>/', PostDetailView.as_view(), name='post_detail'),
]