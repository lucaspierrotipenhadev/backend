from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class FollowUser(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following_relationships'
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follower_relationships'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # Impede registrar a mesma relação de seguir duas vezes
            models.UniqueConstraint(
                fields=['follower', 'following'], 
                name='unique_followers'
            )
        ]
        ordering = ['-created_at']

    def clean(self):
        if self.follower == self.following:
            raise ValidationError("Um usuário não pode seguir a si mesmo.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.follower.username} segue {self.following.username}"