from typing import List, Optional
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from .models import Post, PostMedia

User = get_user_model()


def _infer_media_type(file: UploadedFile) -> str:
    """Acha o tipo de mídia através da extensão do arquivo."""
    name = file.name.lower()
    if name.endswith(('.jpg', '.jpeg', '.png', '.webp')):
        return PostMedia.MediaType.IMAGE
    elif name.endswith(('.mp4', '.mov', '.avi')):
        return PostMedia.MediaType.VIDEO
    elif name.endswith('.gif'):
        return PostMedia.MediaType.GIF
    return PostMedia.MediaType.DOCUMENT

@transaction.atomic
def create_post_with_media(*, author: User, text: str, files: Optional[List[UploadedFile]] = None) -> Post:
    """
    Service para criar um post e anexar suas mídias em uma transação atômica.
    """
    post = Post.objects.create(
        author=author,
        text=text
    )

    if files:
        media_objects = [
            PostMedia(
                post=post,
                file=f,
                media_type=_infer_media_type(f)
            ) for f in files
        ]
        PostMedia.objects.bulk_create(media_objects)

    return post


@transaction.atomic
def update_post(*, post: Post, text: str) -> Post:
    """
    Atualiza o texto do post e sinaliza que ele foi editado.
    """
    if post.text != text:
        post.text = text
        post.edited = True
        post.save()
    return post