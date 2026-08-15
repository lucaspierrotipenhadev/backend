# interactions/services.py
from django.core.exceptions import ValidationError
from .models import PostLike, CommentLike, Comment
from posts.models import Post

class LikeService:
    @staticmethod
    def toggle_post_like(user, post_id) -> bool:
        """
        Alterna a curtida em um post. 
        Retorna True se curtiu, False se removeu a curtida.
        """
        post = Post.objects.filter(id=post_id).first()
        if not post:
            raise ValidationError("Post não encontrado.")

        like, created = PostLike.objects.get_or_create(user=user, post=post)
        if not created:
            like.delete()
            return False
        return True

    @staticmethod
    def toggle_comment_like(user, comment_id) -> bool:
        """
        Alterna a curtida em um comentário.
        Retorna True se curtiu, False se removeu a curtida.
        """
        comment = Comment.objects.filter(id=comment_id).first()
        if not comment:
            raise ValidationError("Comentário não encontrado.")

        like, created = CommentLike.objects.get_or_create(user=user, comment=comment)
        if not created:
            like.delete()
            return False
        return True


class CommentService:
    @staticmethod
    def create_comment(user, post_id: int, text: str, parent_id: int = None) -> Comment:
        """
        Cria um comentário garantindo as validações de post e comentário pai.
        """
        post = Post.objects.filter(id=post_id).first()
        if not post:
            raise ValidationError("Post não encontrado.")

        parent_comment = None
        if parent_id:
            parent_comment = Comment.objects.filter(id=parent_id, post_id=post_id).first()
            if not parent_comment:
                raise ValidationError("Comentário pai não encontrado ou não pertence a este post.")

        return Comment.objects.create(
            author=user,
            post=post,
            parent=parent_comment,
            text=text
        )