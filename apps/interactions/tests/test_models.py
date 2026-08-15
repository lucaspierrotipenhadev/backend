# interactions/tests/test_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.urls import reverse
from rest_framework.test import APITestCase
from posts.models import Post
from interactions.models import Comment, PostLike, CommentLike 

User = get_user_model()

class CommentViewSetTests(APITestCase):
    def setUp(self):
        # Adicione emails explicitamente para evitar colisões
        self.user = User.objects.create_user(
            username='author', 
            email='author@example.com', 
            password='password123'
        )
        self.other_user = User.objects.create_user(
            username='other', 
            email='other@example.com', 
            password='password123'
        )
        self.post = Post.objects.create(author=self.user, text='Publicação para comentários')
        self.comment_list_url = reverse('comment-list')
    
    def test_comment_creation_and_str(self):
        comment = Comment.objects.create(
            author=self.user,
            post=self.post,
            text='Ótimo post!'
        )
        self.assertEqual(str(comment), f"Comment by {self.user.username} on Post {self.post.id}")
        self.assertIsNone(comment.parent)

    def test_nested_comment_reply(self):
        parent_comment = Comment.objects.create(
            author=self.user,
            post=self.post,
            text='Comentário pai'
        )
        child_comment = Comment.objects.create(
            author=self.user,
            post=self.post,
            parent=parent_comment,
            text='Resposta ao comentário'
        )
        self.assertEqual(child_comment.parent, parent_comment)
        self.assertIn(child_comment, parent_comment.replies.all())

    def test_unique_post_like_constraint(self):
        PostLike.objects.create(user=self.user, post=self.post)
        # Tentar curtir o mesmo post novamente deve disparar erro de integridade
        with self.assertRaises(IntegrityError):
            PostLike.objects.create(user=self.user, post=self.post)

    def test_unique_comment_like_constraint(self):
        comment = Comment.objects.create(author=self.user, post=self.post, text='Texto')
        CommentLike.objects.create(user=self.user, comment=comment)
        
        with self.assertRaises(IntegrityError):
            CommentLike.objects.create(user=self.user, comment=comment)