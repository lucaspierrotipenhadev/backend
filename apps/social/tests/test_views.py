# apps/social/tests/test_views.py
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from social.models import FollowUser

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_a(db):
    return User.objects.create_user(
        username='user_a', 
        email='a@example.com', 
        password='Password123!'
    )


@pytest.fixture
def user_b(db):
    return User.objects.create_user(
        username='user_b', 
        email='b@example.com', 
        password='Password123!'
    )


@pytest.mark.django_db
class TestSocialEndpoints:

    def test_toggle_follow_unauthenticated_fails(self, api_client, user_b):
        """Requisição sem token de autenticação deve retornar 401."""
        url = reverse('social:toggle-follow', kwargs={'user_id': user_b.id})
        response = api_client.post(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_toggle_follow_success(self, api_client, user_a, user_b):
        """Usuário autenticado segue com sucesso outro usuário (200 OK)."""
        api_client.force_authenticate(user=user_a)
        url = reverse('social:toggle-follow', kwargs={'user_id': user_b.id})

        response = api_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_following'] is True
        assert FollowUser.objects.filter(follower=user_a, following=user_b).exists()

    def test_list_followers_view(self, api_client, user_a, user_b):
        """Verifica se a listagem de seguidores de um usuário retorna a lista correta."""
        # User A segue User B
        FollowUser.objects.create(follower=user_a, following=user_b)

        api_client.force_authenticate(user=user_a)
        url = reverse('social:user-followers', kwargs={'user_id': user_b.id})

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1 if 'results' in response.data else len(response.data) == 1
        
        # Pega a lista tratada com ou sem paginação
        data = response.data.get('results', response.data)
        assert data[0]['username'] == 'user_a'

    def test_list_following_view(self, api_client, user_a, user_b):
        """Verifica se a listagem de quem o usuário segue retorna corretamente."""
        FollowUser.objects.create(follower=user_a, following=user_b)

        api_client.force_authenticate(user=user_a)
        url = reverse('social:user-following', kwargs={'user_id': user_a.id})

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        
        data = response.data.get('results', response.data)
        assert len(data) == 1
        assert data[0]['username'] == 'user_b'