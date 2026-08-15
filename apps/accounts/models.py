from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User Model para garantir flexibilidade futura.
    Utiliza o email como dado único importante além do username.
    """
    email = models.EmailField('E-mail', unique=True)

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username


class Profile(models.Model):
    """
    Perfil do usuário contendo dados públicos e de apresentação.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    display_name = models.CharField('Nome de exibição', max_length=100, blank=True)
    bio = models.TextField('Biografia', max_length=500, blank=True)
    avatar = models.ImageField('Foto de perfil', upload_to='avatars/', null=True, blank=True)
    birth_date = models.DateField('Data de nascimento', null=True, blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"