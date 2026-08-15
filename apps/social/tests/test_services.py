# apps/social/tests/test_services.py
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from social.models import FollowUser
from social.services import FollowService

User = get_user_model()


@pytest.mark.django_db
class TestFollowService:

    def test_toggle_follow_creates_relationship(self, user_a, user_b):
        """Verifica se o serviço cria a relação de seguir e retorna True."""
        is_following = FollowService.toggle_follow(
            follower=user_a, 
            following_id=user_b.id
        )

        assert is_following is True
        assert FollowUser.objects.filter(follower=user_a, following=user_b).exists()

    def test_toggle_follow_removes_existing_relationship(self, user_a, user_b):
        """Verifica se o serviço remove a relação existente e retorna False."""
        # Cria a relação inicial
        FollowUser.objects.create(follower=user_a, following=user_b)

        # Executa o toggle para deixar de seguir
        is_following = FollowService.toggle_follow(
            follower=user_a, 
            following_id=user_b.id
        )

        assert is_following is False
        assert not FollowUser.objects.filter(follower=user_a, following=user_b).exists()

    def test_prevent_user_from_following_themselves(self, user_a):
        """Garante que um usuário não pode seguir a si mesmo."""
        with pytest.raises(ValidationError):
            FollowService.toggle_follow(
                follower=user_a, 
                following_id=user_a.id
            )