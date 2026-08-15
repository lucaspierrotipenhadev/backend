# interactions/tests/test_services.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from posts.models import Post
from interactions.models import Comment, PostLike, CommentLike
from interactions.services import LikeService, CommentService

User = get_user_model()

class InteractionServicesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='password123')
        self.post = Post.objects.create(author=self.user, text='Test Post')

    def test_toggle_post_like_service(self):
        # 1. Primeira chamada -> Curte (retorna True)
        is_liked = LikeService.toggle_post_like(user=self.user, post_id=self.post.id)
        self.assertTrue(is_liked)
        self.assertEqual(PostLike.objects.count(), 1)

        # 2. Segunda chamada -> Remove curtida (retorna False)
        is_liked = LikeService.toggle_post_like(user=self.user, post_id=self.post.id)
        self.assertFalse(is_liked)
        self.assertEqual(PostLike.objects.count(), 0)

    def test_toggle_post_like_invalid_post_raises_error(self):
        with self.assertRaises(ValidationError):
            LikeService.toggle_post_like(user=self.user, post_id=9999)

    def test_create_comment_service_success(self):
        comment = CommentService.create_comment(
            user=self.user,
            post_id=self.post.id,
            text='Comentário via Service'
        )
        self.assertEqual(comment.text, 'Comentário via Service')
        self.assertEqual(comment.author, self.user)

    def test_create_reply_to_different_post_comment_raises_error(self):
        other_post = Post.objects.create(author=self.user, text='Outro Post')
        parent_comment = Comment.objects.create(author=self.user, post=other_post, text='Pai de outro post')

        # Tentar vincular a resposta a um post, mas apontar o pai para um comentário de OUTRO post
        with self.assertRaises(ValidationError):
            CommentService.create_comment(
                user=self.user,
                post_id=self.post.id,
                text='Resposta inválida',
                parent_id=parent_comment.id
            )