from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class AccountsAPITests(APITestCase):

    def setUp(self):
        # Dados padrão para reaproveitar nos testes
        self.register_url = reverse('accounts:register')
        self.token_url = reverse('accounts:token_obtain_pair')
        self.me_url = reverse('accounts:me')
        self.update_profile_url = reverse('accounts:update_profile')

        self.user_data = {
            'username': 'lucasdev',
            'email': 'lucas@example.com',
            'password': 'Password123!',
            'password_confirm': 'Password123!',
            'display_name': 'Lucas Dev'
        }

    def test_register_user_success(self):
        """Garante que um novo usuário e seu perfil são criados com sucesso."""
        response = self.client.post(self.register_url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        
        # Verifica se o perfil também foi criado automaticamente pelo Service
        user = User.objects.get(username='lucasdev')
        self.assertEqual(user.profile.display_name, 'Lucas Dev')

    def test_register_password_mismatch_fails(self):
        """Garante que o registro falha se as senhas não coincidirem."""
        invalid_data = self.user_data.copy()
        invalid_data['password_confirm'] = 'Diferente123!'

        response = self.client.post(self.register_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_obtain_token_and_access_protected_route(self):
        """Testa o login JWT e o acesso à rota autenticada /me/."""
        # 1. Registra o usuário
        self.client.post(self.register_url, self.user_data, format='json')

        # 2. Faz login para obter os tokens
        login_data = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        token_response = self.client.post(self.token_url, login_data, format='json')
        
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', token_response.data)
        self.assertIn('refresh', token_response.data)

        access_token = token_response.data['access']

        # 3. Tenta acessar /me/ SEM o token (deve falhar 401)
        unauthorized_response = self.client.get(self.me_url)
        self.assertEqual(unauthorized_response.status_code, status.HTTP_401_UNAUTHORIZED)

        # 4. Acessa /me/ COM o token no Header (deve retornar 200 OK)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        authorized_response = self.client.get(self.me_url)

        self.assertEqual(authorized_response.status_code, status.HTTP_200_OK)
        self.assertEqual(authorized_response.data['username'], self.user_data['username'])

    def test_update_profile(self):
        """Testa a atualização dos dados do perfil do usuário logado."""
        # Registra e autentica
        self.client.post(self.register_url, self.user_data, format='json')
        
        login_response = self.client.post(self.token_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }, format='json')
        
        token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Atualiza a Bio e o Display Name
        patch_data = {
            'display_name': 'Lucas Engenheiro',
            'bio': 'Desenvolvedor Backend Python/Django'
        }
        response = self.client.patch(self.update_profile_url, patch_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['display_name'], 'Lucas Engenheiro')
        self.assertEqual(response.data['bio'], 'Desenvolvedor Backend Python/Django')