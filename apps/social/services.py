from django.contrib.auth.models import User
from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from .models import FollowUser

User = get_user_model()

class FollowService:
    @staticmethod
    @transaction.atomic
    def toggle_follow(*, follower: User, following_id: int) -> bool:
        """
        Alterna o status de seguir:
        - Se já segue, remove o relacionamento (retorna False)
        - Se não segue, cria o relacionamento (retorna True)
        """
        if follower.id == following_id:
            raise ValidationError({"detail": "Você não pode seguir a si mesmo."})

        following = get_object_or_404(User, id=following_id)

        follow_instance = FollowUser.objects.filter(
            follower=follower, 
            following=following
        ).first()

        if follow_instance:
            follow_instance.delete()
            return False
        
        FollowUser.objects.create(follower=follower, following=following)
        return True