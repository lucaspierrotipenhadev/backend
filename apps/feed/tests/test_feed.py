# apps/social/tests/test_feed.py
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from posts.models import Post
from social.models import FollowUser

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_a(db):
    return User.objects.create_user(username='user_a', email='a@example.com', password='Password123!')


@pytest.fixture
def user_b(db):
    return User.objects.create_user(username='user_b', email='b@example.com', password='Password123!')


@pytest.fixture
def user_c(db):
    return User.objects.create_user(username='user_c', email='c@example.com', password='Password123!')


@pytest.mark.django_db
class TestFeedEndpoint:

    def test_feed_shows_own_and_followed_posts_only(self, api_client, user_a, user_b, user_c):
        """
        O feed do User A deve conter:
        - Posts do User A (ele mesmo)
        - Posts do User B (quem ele segue)
        E NÃO deve conter:
        - Posts do User C (quem ele NÃO segue)
        """
        post_a = Post.objects.create(author=user_a, text="Post do User A")
        post_b = Post.objects.create(author=user_b, text="Post do User B")
        post_c = Post.objects.create(author=user_c, text="Post do User C")

        # User A segue apenas User B
        FollowUser.objects.create(follower=user_a, following=user_b)

        api_client.force_authenticate(user=user_a)
        url = reverse('social:feed')

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        
        post_ids = [post['id'] for post in results]
        assert len(post_ids) == 2
        assert post_a.id in post_ids
        assert post_b.id in post_ids
        assert post_c.id not in post_ids