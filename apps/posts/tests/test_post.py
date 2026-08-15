from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.services import create_user_with_profile
from posts.models import Post

User = get_user_model()


class PostsAPITestCase(APITestCase):

    def setUp(self):
        self.user1 = create_user_with_profile(
            username='autor1',
            email='autor1@example.com',
            password='Password123!'
        )
        self.user2 = create_user_with_profile(
            username='outro_user',
            email='outro@example.com',
            password='Password123!'
        )

        self.list_create_url = reverse('posts:post_list_create')

    def _authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_create_post_success(self):
        """Garante a criação de post com sucesso por um usuário autenticado."""
        self._authenticate(self.user1)

        data = {'text': 'Meu primeiro post no FakeSocial!'}
        response = self.client.post(self.list_create_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(response.data['text'], 'Meu primeiro post no FakeSocial!')
        self.assertEqual(response.data['author']['username'], 'autor1')

    def test_create_post_with_media(self):
        """Testa o envio de post contendo arquivo de imagem em anexo."""
        self._authenticate(self.user1)

        image_file = SimpleUploadedFile(
            "test_image.jpg", 
            b"file_content", 
            content_type="image/jpeg"
        )

        data = {
            'text': 'Post com mídia',
            'files': [image_file]
        }
        
        response = self.client.post(self.list_create_url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['medias']), 1)
        self.assertEqual(response.data['medias'][0]['media_type'], 'IMAGE')

    def test_unauthenticated_user_cannot_create_post(self):
        """Garante que usuários não logados recebem 401 ao tentar publicar."""
        data = {'text': 'Tentativa anônima'}
        response = self.client.post(self.list_create_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_post_only_by_author(self):
        """Garante que apenas o próprio autor consegue editar o post e atualiza a flag 'edited'."""
        self._authenticate(self.user1)
        post_response = self.client.post(self.list_create_url, {'text': 'Texto original'}, format='json')
        post_id = post_response.data['id']
        detail_url = reverse('posts:post_detail', kwargs={'pk': post_id})

        # Tentativa de edição pelo user2 (Outro autor)
        self._authenticate(self.user2)
        patch_response = self.client.patch(detail_url, {'text': 'Texto alterado'}, format='json')
        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)

        # Edição pelo autor real (user1)
        self._authenticate(self.user1)
        patch_response = self.client.patch(detail_url, {'text': 'Texto alterado com sucesso'}, format='json')
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['text'], 'Texto alterado com sucesso')
        self.assertTrue(patch_response.data['edited'])

    def test_delete_post_only_by_author(self):
        """Garante que apenas o autor pode deletar seu próprio post."""
        self._authenticate(self.user1)
        post_response = self.client.post(self.list_create_url, {'text': 'Texto a ser deletado'}, format='json')
        post_id = post_response.data['id']
        detail_url = reverse('posts:post_detail', kwargs={'pk': post_id})

        # user2 tenta deletar -> Negado (403)
        self._authenticate(self.user2)
        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)

        # user1 deleta -> Sucesso (204)
        self._authenticate(self.user1)
        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 0)