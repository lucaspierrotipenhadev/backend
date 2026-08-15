from django.db import transaction
from .models import User, Profile


@transaction.atomic
def create_user_with_profile(*, username: str, email: str, password: str, display_name: str = '') -> User:
    """
    Service para registrar um usuário e criar automaticamente seu Profile vinculado em uma transação atômica.
    """
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    Profile.objects.create(
        user=user,
        display_name=display_name or username
    )

    return user