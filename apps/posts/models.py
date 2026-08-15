from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='posts'
    )
    text = models.TextField('Texto do Post', max_length=280)
    edited = models.BooleanField('Editado', default=False)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Post #{self.id} por {self.author.username}"


class PostMedia(models.Model):
    class MediaType(models.TextChoices):
        IMAGE = 'IMAGE', 'Imagem'
        VIDEO = 'VIDEO', 'Vídeo'
        GIF = 'GIF', 'GIF'
        DOCUMENT = 'DOCUMENT', 'Documento'

    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='medias'
    )
    file = models.FileField('Arquivo', upload_to='posts/media/')
    media_type = models.CharField(
        'Tipo de Mídia', 
        max_length=10, 
        choices=MediaType.choices, 
        default=MediaType.IMAGE
    )
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    def __str__(self):
        return f"Mídia ({self.media_type}) do Post #{self.post.id}"