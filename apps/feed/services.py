# apps/social/services.py
from django.db.models import QuerySet, Exists, OuterRef, Count
from django.contrib.auth import get_user_model
from posts.models import Post
from interactions.models import PostLike
from social.models import FollowUser

User = get_user_model()


class FeedService:
    @staticmethod
    def get_user_feed(user: User) -> QuerySet[Post]:
        """
        Retorna as publicações dos usuários que o usuário logado segue, 
        incluindo as próprias publicações, ordenadas do mais recente para o mais antigo.
        Aplica otimizações para evitar N+1 queries.
        """
        # IDs dos usuários seguidos + ID do próprio usuário
        following_ids = FollowUser.objects.filter(
            follower=user
        ).values_list('following_id', flat=True)
        
        allowed_user_ids = list(following_ids) + [user.id]

        # Subqueries para verificar se o usuário atual curtiu cada post
        user_likes_subquery = PostLike.objects.filter(
            post=OuterRef('pk'), 
            user=user
        )

        # Montagem do QuerySet otimizado
        return (
            Post.objects.filter(author_id__in=allowed_user_ids)
            .select_related('author', 'author__profile')
            .prefetch_related('medias')  # Pré-carrega as mídias associadas (PostMedia)
            .annotate(
                likes_count=Count('likes', distinct=True),
                comments_count=Count('comments', distinct=True),
                has_liked=Exists(user_likes_subquery),
            )
            .order_by('-created_at')
        )