# interactions/tests/test_views.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from posts.models import Post
from interactions.models import Comment, PostLike

User = get_user_model()

class CommentViewSetTests(APITestCase):
    def setUp(self):
        # Provide unique emails to prevent UNIQUE constraint collisions on accounts_user.email
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

    def test_create_comment_authenticated(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            'post': self.post.id,
            'text': 'Novo comentário via API'
        }
        response = self.client.post(self.comment_list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)

    def test_create_comment_unauthenticated_fails(self):
        payload = {
            'post': self.post.id,
            'text': 'Comentário anônimo'
        }
        response = self.client.post(self.comment_list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_other_user_comment_forbidden(self):
        comment = Comment.objects.create(author=self.user, post=self.post, text='Texto original')
        comment_detail_url = reverse('comment-detail', kwargs={'pk': comment.id})

        # Autentica como OUTRO usuário e tenta editar
        self.client.force_authenticate(user=self.other_user)
        payload = {'text': 'Texto alterado por terceiros'}
        response = self.client.patch(comment_detail_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class LikeEndpointsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='liker', 
            email='liker@example.com', 
            password='password123'
        )
        self.post = Post.objects.create(author=self.user, text='Post para curtir')
        self.comment = Comment.objects.create(author=self.user, post=self.post, text='Comentário para curtir')
        
        self.post_like_url = reverse('post-like', kwargs={'post_id': self.post.id})
        self.comment_like_url = reverse('comment-like', kwargs={'pk': self.comment.id})

    def test_toggle_post_like_endpoint(self):
        self.client.force_authenticate(user=self.user)

        # 1. Curtir
        res1 = self.client.post(self.post_like_url)
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertTrue(res1.data['is_liked'])

        # 2. Descurtir
        res2 = self.client.post(self.post_like_url)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertFalse(res2.data['is_liked'])

    def test_toggle_comment_like_endpoint(self):
        self.client.force_authenticate(user=self.user)

        # Curtir comentário
        response = self.client.post(self.comment_like_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_liked'])