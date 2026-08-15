# interactions/utils.py
from .models import PostLike, CommentLike

def get_user_liked_post_ids(user, post_ids):
    """
    Retorna um set com os IDs dos posts que o usuário curtiu dentro de uma lista dada.
    """
    if not user.is_authenticated:
        return set()
    return set(
        PostLike.objects.filter(user=user, post_id__in=post_ids)
        .values_list('post_id', flat=True)
    )

def get_user_liked_comment_ids(user, comment_ids):
    """
    Retorna um set com os IDs dos comentários que o usuário curtiu dentro de uma lista dada.
    """
    if not user.is_authenticated:
        return set()
    return set(
        CommentLike.objects.filter(user=user, comment_id__in=comment_ids)
        .values_list('comment_id', flat=True)
    )