🏗️ Documentação da Arquitetura - Backend Django REST
Versão: 1.0.0
Última atualização: Agosto 2026
Tecnologia: Python 3.x + Django REST Framework

📋 Índice
- Visão Geral
    -Estrutura de Apps
    -Model
    -Services
    -Serializers
    -ViewSets
    -Urls
    -Tests
    -Admin
    -Estrutura de Pastas
    -Fluxo de Exemplo: Criação de Perfil
    -Padrões de Nomenclatura
    -Autenticação e Segurança
    -Testes
    -Benefícios da Arquitetura
    -Considerações Finais

*Visão Geral*
- O sistema foi desenvolvido com uma arquitetura baseada em apps modulares no Django, onde cada app é responsável por uma funcionalidade específica do sistema. Esta abordagem segue os princípios do Domain-Driven Design (DDD) e da Clean Architecture adaptados para o ecossistema Django, garantindo:
    Separação clara de responsabilidades
    Alta testabilidade
    Manutenção facilitada
    Escalabilidade para novos recursos
    Reutilização de código

- O sistema é composto por 5 apps principais:
App	            Responsabilidade
Accounts	    Gerenciamento de usuários, perfis, autenticação e autorização
Posts	        Criação, edição, exclusão e listagem de posts
Feed	        Algoritmo de feed personalizado e curadoria de conteúdo
Interactions	Curtidas, comentários, compartilhamentos e outras interações
Social	        Conexões entre usuários (seguir/deixar de seguir), rede social

*Estrutura de Apps*
- Cada app segue uma estrutura padronizada com 7 componentes principais:
-----------------------------------------------------------------------
text
app_name/
├── __init__.py
├── admin.py         # Configuração do Django Admin
├── apps.py          # Configuração do app
├── models.py        # Definição dos modelos de dados
├── serializers.py   # Conversão de dados (JSON ↔ Model)
├── services.py      # Lógica de negócio
├── tests.py         # Testes unitários e de integração
├── urls.py          # Rotas do app
└── viewsets.py      # Controladores das requisições
-----------------------------------------------------------------------

1. Model
O Model é a representação da estrutura de dados no banco de dados. Ele define os campos, relacionamentos, validações e métodos auxiliares.

🎯 Responsabilidades:
    Definir a estrutura da tabela no banco de dados
    Estabelecer relacionamentos entre tabelas (ForeignKey, ManyToMany, OneToOne)
    Implementar validações em nível de banco de dados
    Fornecer métodos auxiliares para manipulação dos dados

📝 Exemplo:
python
****************************************************************************************
# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator

class User(AbstractUser):
    """Modelo personalizado de usuário"""
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']
        
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_complete_profile(self):
        """Verifica se o perfil está completo"""
        return bool(self.first_name and self.last_name and self.email)

class UserProfile(models.Model):
    """Perfil estendido do usuário"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])]
    )
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    posts_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'user_profiles'
        
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    def increment_followers(self):
        """Incrementa contador de seguidores"""
        self.followers_count += 1
        self.save(update_fields=['followers_count'])
    
    def decrement_followers(self):
        """Decrementa contador de seguidores"""
        self.followers_count -= 1
        self.save(update_fields=['followers_count'])
****************************************************************************************

2. Services
O Services contém a lógica de negócio da aplicação. É o local onde implementamos regras de negócio, validações complexas e orquestração de operações.

🎯 Responsabilidades:
    Implementar regras de negócio complexas
    Orquestrar operações que envolvem múltiplos modelos
    Realizar validações que vão além do nível do modelo
    Manter o ViewSet limpo e com pouca lógica

📝 Exemplo:
python
****************************************************************************************
# accounts/services.py
from django.core.exceptions import ValidationError
from django.db import transaction
from django.core.files.storage import default_storage
from typing import Optional
from .models import User, UserProfile
from .serializers import UserProfileSerializer

class UserService:
    """Serviço para gerenciar operações relacionadas a usuários"""
    
    @staticmethod
    def create_user_with_profile(user_data: dict, profile_data: dict) -> User:
        """
        Cria um usuário e seu perfil em uma única transação
        """
        with transaction.atomic():
            # Criação do usuário
            user = User.objects.create_user(**user_data)
            
            # Criação do perfil
            UserProfile.objects.create(
                user=user,
                **profile_data
            )
            
            return user
    
    @staticmethod
    def update_profile(user: User, profile_data: dict) -> UserProfile:
        """
        Atualiza o perfil do usuário com validações
        """
        profile = user.profile
        
        # Validações de negócio
        if 'bio' in profile_data and len(profile_data['bio']) > 500:
            raise ValidationError('Bio não pode ter mais de 500 caracteres')
        
        # Atualiza campos permitidos
        allowed_fields = ['bio', 'location', 'website', 'birth_date']
        for field in allowed_fields:
            if field in profile_data:
                setattr(profile, field, profile_data[field])
        
        profile.save()
        return profile
    
    @staticmethod
    def upload_avatar(user: User, avatar_file) -> UserProfile:
        """
        Faz upload e processa o avatar do usuário
        """
        profile = user.profile
        
        # Validação do arquivo
        if avatar_file.size > 5 * 1024 * 1024:  # 5MB
            raise ValidationError('A imagem não pode ter mais de 5MB')
        
        # Delete avatar antigo se existir
        if profile.avatar:
            default_storage.delete(profile.avatar.name)
        
        # Salva novo avatar
        profile.avatar = avatar_file
        profile.save()
        
        return profile
    
    @staticmethod
    def get_user_by_token(token: str) -> Optional[User]:
        """
        Busca usuário pelo token de autenticação
        """
        from rest_framework.authtoken.models import Token
        
        try:
            token_obj = Token.objects.select_related('user').get(key=token)
            return token_obj.user
        except Token.DoesNotExist:
            return None
    
    @staticmethod
    def get_full_profile(user: User) -> dict:
        """
        Retorna dados completos do perfil com estatísticas
        """
        profile = user.profile
        
        return {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name(),
                'date_joined': user.date_joined,
            },
            'profile': {
                'bio': profile.bio,
                'avatar': profile.avatar.url if profile.avatar else None,
                'location': profile.location,
                'website': profile.website,
                'birth_date': profile.birth_date,
                'followers_count': profile.followers_count,
                'following_count': profile.following_count,
                'posts_count': profile.posts_count,
            },
            'stats': {
                'is_profile_complete': user.is_complete_profile,
                'account_verified': user.is_verified,
            }
        }
****************************************************************************************

3. Serializers
O Serializer é responsável pela conversão entre dados JSON e objetos Python (Model), além de fornecer validação de dados.

🎯 Responsabilidades:
    Validar dados de entrada
    Converter Model ↔ JSON
    Controlar quais campos são expostos na API
    Implementar validações específicas de campo

📝 Exemplo:
python
****************************************************************************************
# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile

class UserSerializer(serializers.ModelSerializer):
    """Serializer básico para usuário"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'date_joined', 'is_verified']
        read_only_fields = ['id', 'date_joined', 'is_verified']

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para o perfil do usuário"""
    
    class Meta:
        model = UserProfile
        fields = ['id', 'bio', 'avatar', 'location', 'website', 
                  'birth_date', 'followers_count', 'following_count', 
                  'posts_count']
        read_only_fields = ['id', 'followers_count', 'following_count', 
                           'posts_count']

class RegisterSerializer(serializers.Serializer):
    """Serializer para registro de novos usuários"""
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=50, required=False)
    last_name = serializers.CharField(max_length=50, required=False)
    
    def validate(self, data):
        """Validação global do serializer"""
        # Verifica se as senhas coincidem
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'As senhas não coincidem'
            })
        
        # Verifica se email já existe
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({
                'email': 'Este email já está cadastrado'
            })
        
        # Verifica se username já existe
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({
                'username': 'Este nome de usuário já está em uso'
            })
        
        return data
    
    def create(self, validated_data):
        """Cria o usuário a partir dos dados validados"""
        # Remove password_confirm antes de criar o usuário
        validated_data.pop('password_confirm')
        
        user = User.objects.create_user(**validated_data)
        
        # Cria perfil padrão
        UserProfile.objects.create(user=user)
        
        return user

class AvatarUploadSerializer(serializers.Serializer):
    """Serializer para upload de avatar"""
    avatar = serializers.ImageField()
    
    def validate_avatar(self, value):
        """Validação específica para o avatar"""
        # Valida tamanho (5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError(
                'A imagem não pode ter mais que 5MB'
            )
        
        # Valida extensão
        allowed_extensions = ['jpg', 'jpeg', 'png']
        extension = value.name.split('.')[-1].lower()
        if extension not in allowed_extensions:
            raise serializers.ValidationError(
                f'Formato de imagem inválido. Use: {", ".join(allowed_extensions)}'
            )
        
        return value

class LoginSerializer(serializers.Serializer):
    """Serializer para login"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
****************************************************************************************

4. ViewSets
O ViewSet é o controlador que gerencia as requisições HTTP, coordenando a interação entre o Serializer e os Services.

🎯 Responsabilidades:
    Receber e processar requisições HTTP
    Controlar autenticação e permissões
    Chamar os Services para executar a lógica de negócio
    Retornar respostas HTTP apropriadas

📝 Exemplo:
python
****************************************************************************************
# accounts/viewsets.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import authenticate
from .models import User
from .serializers import (
    UserSerializer, UserProfileSerializer, RegisterSerializer,
    LoginSerializer, AvatarUploadSerializer
)
from .services import UserService

class AuthViewSet(viewsets.GenericViewSet):
    """ViewSet para autenticação e registro"""
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['POST'])
    def register(self, request):
        """Registro de novo usuário"""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        
        # Cria token de autenticação
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['POST'])
    def login(self, request):
        """Login de usuário"""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        
        if not user:
            return Response({
                'error': 'Credenciais inválidas'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Atualiza token
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        })
    
    @action(detail=False, methods=['POST'])
    def logout(self, request):
        """Logout (delete token)"""
        request.user.auth_token.delete()
        return Response({'message': 'Logout realizado com sucesso'})

class ProfileViewSet(viewsets.GenericViewSet):
    """ViewSet para gerenciamento de perfil"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['GET'])
    def me(self, request):
        """Retorna perfil do usuário autenticado"""
        user = request.user
        profile_data = UserService.get_full_profile(user)
        return Response(profile_data)
    
    @action(detail=False, methods=['PATCH'])
    def update(self, request):
        """Atualiza perfil do usuário"""
        user = request.user
        
        # Atualiza dados do usuário
        user_serializer = UserSerializer(
            user, 
            data=request.data, 
            partial=True
        )
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        
        # Atualiza dados do perfil
        profile = UserService.update_profile(
            user, 
            request.data
        )
        
        return Response({
            'user': UserSerializer(user).data,
            'profile': UserProfileSerializer(profile).data
        })
    
    @action(detail=False, methods=['POST'], url_path='upload-avatar')
    def upload_avatar(self, request):
        """Upload de avatar do usuário"""
        serializer = AvatarUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        profile = UserService.upload_avatar(
            request.user, 
            serializer.validated_data['avatar']
        )
        
        return Response({
            'avatar': profile.avatar.url if profile.avatar else None,
            'message': 'Avatar atualizado com sucesso'
        })
    
    @action(detail=False, methods=['GET'])
    def stats(self, request):
        """Retorna estatísticas do usuário"""
        user = request.user
        profile = user.profile
        
        return Response({
            'posts_count': profile.posts_count,
            'followers_count': profile.followers_count,
            'following_count': profile.following_count,
            'is_profile_complete': user.is_complete_profile,
            'joined_days': (timezone.now() - user.date_joined).days
        })
    
    @action(detail=True, methods=['GET'])
    def public(self, request, pk=None):
        """Retorna perfil público de outro usuário"""
        try:
            user = User.objects.get(id=pk)
            profile_data = UserService.get_full_profile(user)
            return Response(profile_data)
        except User.DoesNotExist:
            return Response({
                'error': 'Usuário não encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
****************************************************************************************

5. Urls
O Urls define as rotas (endpoints) da API, mapeando as URLs para os ViewSets.

🎯 Responsabilidades:
    Definir as rotas da API
    Mapear endpoints para ViewSets
    Configurar routers automáticos

📝 Exemplo:
python
****************************************************************************************
# accounts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import AuthViewSet, ProfileViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'profile', ProfileViewSet, basename='profile')

urlpatterns = [
    # Rotas automáticas do router
    path('', include(router.urls)),
    
    # Rotas manuais (se necessário)
    # path('profile/<int:pk>/public/', ProfileViewSet.as_view({'get': 'public'})),
]
****************************************************************************************

# URLs disponíveis:
# POST /api/accounts/auth/register/
# POST /api/accounts/auth/login/
# POST /api/accounts/auth/logout/
# GET  /api/accounts/profile/me/
# PATCH /api/accounts/profile/update/
# POST /api/accounts/profile/upload-avatar/
# GET  /api/accounts/profile/stats/
# GET  /api/accounts/profile/{id}/public/

6. Tests
Os Tests garantem a qualidade do código, validando o comportamento de cada componente.

🎯 Responsabilidades:
    Validar regras de negócio
    Testar endpoints da API
    Verificar validações de dados
    Garantir cobertura de código

📝 Exemplo:
python
****************************************************************************************
# accounts/tests.py
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

class AuthTests(TestCase):
    """Testes para autenticação"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/accounts/auth/register/'
        self.login_url = '/api/accounts/auth/login/'
        
    def test_register_success(self):
        """Teste de registro bem-sucedido"""
        data = {
            'username': 'testuser',
            'email': 'test@email.com',
            'password': 'Test@123456',
            'password_confirm': 'Test@123456',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = self.client.post(self.register_url, data)
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        
        # Verifica se o usuário foi criado
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@email.com')
        
        # Verifica se o perfil foi criado
        self.assertTrue(hasattr(user, 'profile'))
    
    def test_register_password_mismatch(self):
        """Teste de registro com senhas diferentes"""
        data = {
            'username': 'testuser',
            'email': 'test@email.com',
            'password': 'Test@123456',
            'password_confirm': 'Different@123456',
        }
        
        response = self.client.post(self.register_url, data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('password_confirm', response.data)
    
    def test_register_duplicate_email(self):
        """Teste de registro com email duplicado"""
        # Cria usuário inicial
        User.objects.create_user(
            username='user1',
            email='test@email.com',
            password='Test@123456'
        )
        
        # Tenta criar outro com mesmo email
        data = {
            'username': 'user2',
            'email': 'test@email.com',
            'password': 'Test@123456',
            'password_confirm': 'Test@123456',
        }
        
        response = self.client.post(self.register_url, data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)
    
    def test_login_success(self):
        """Teste de login bem-sucedido"""
        # Cria usuário
        user = User.objects.create_user(
            username='testuser',
            password='Test@123456'
        )
        
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'Test@123456'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)

class ProfileTests(TestCase):
    """Testes para perfil do usuário"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Cria usuário e token
        self.user = User.objects.create_user(
            username='testuser',
            email='test@email.com',
            password='Test@123456'
        )
        self.token = Token.objects.create(user=self.user)
        
        # Autentica
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
    
    def test_get_profile(self):
        """Teste de obtenção do perfil"""
        response = self.client.get('/api/accounts/profile/me/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_update_profile(self):
        """Teste de atualização do perfil"""
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'This is my bio',
            'location': 'São Paulo'
        }
        
        response = self.client.patch('/api/accounts/profile/update/', data)
        
        self.assertEqual(response.status_code, 200)
        
        # Verifica se foi atualizado
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.profile.bio, 'This is my bio')
    
    def test_upload_avatar(self):
        """Teste de upload de avatar"""
        # Cria arquivo de imagem mock
        avatar = SimpleUploadedFile(
            name='avatar.jpg',
            content=b'fake_image_content',
            content_type='image/jpeg'
        )
        
        response = self.client.post(
            '/api/accounts/profile/upload-avatar/',
            {'avatar': avatar},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('avatar', response.data)
        
        # Verifica se o avatar foi salvo
        self.user.profile.refresh_from_db()
        self.assertIsNotNone(self.user.profile.avatar)
    
    def test_avatar_size_limit(self):
        """Teste de limite de tamanho do avatar"""
        # Cria arquivo grande (6MB)
        large_avatar = SimpleUploadedFile(
            name='large.jpg',
            content=b'0' * (6 * 1024 * 1024),  # 6MB
            content_type='image/jpeg'
        )
        
        response = self.client.post(
            '/api/accounts/profile/upload-avatar/',
            {'avatar': large_avatar},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('avatar', response.data)
    
    def test_get_public_profile(self):
        """Teste de obtenção de perfil público"""
        # Cria outro usuário
        other_user = User.objects.create_user(
            username='otheruser',
            password='Test@123456'
        )
        
        response = self.client.get(
            f'/api/accounts/profile/{other_user.id}/public/'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['username'], 'otheruser')
    
    def test_public_profile_not_found(self):
        """Teste de perfil público inexistente"""
        response = self.client.get('/api/accounts/profile/999/public/')
        
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.data)
****************************************************************************************

7. Admin
O Admin configura a interface administrativa do Django, permitindo o gerenciamento dos dados de forma intuitiva.

🎯 Responsabilidades:
    Configurar a visualização no Django Admin
    Adicionar funcionalidades de busca e filtro
    Criar ações em massa
    Personalizar a interface administrativa

📝 Exemplo:
python
****************************************************************************************
# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile

class UserProfileInline(admin.StackedInline):
    """Inline para exibir o perfil dentro do usuário"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fields = ['avatar', 'bio', 'location', 'website', 
              'birth_date', 'followers_count', 'following_count', 
              'posts_count']
    readonly_fields = ['followers_count', 'following_count', 'posts_count']

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin personalizado para o modelo User"""
    list_display = ['username', 'email', 'first_name', 'last_name', 
                    'is_verified', 'is_active', 'date_joined']
    list_filter = ['is_verified', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['date_joined', 'last_login']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {
            'fields': ('phone', 'is_verified')
        }),
    )
    
    inlines = [UserProfileInline]
    
    actions = ['mark_as_verified', 'send_verification_email']
    
    def mark_as_verified(self, request, queryset):
        """Ação para marcar usuários como verificados"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} usuários marcados como verificados')
    mark_as_verified.short_description = 'Marcar usuários como verificados'
    
    def send_verification_email(self, request, queryset):
        """Ação para enviar email de verificação"""
        # Lógica para enviar email
        self.message_user(request, f'Emails enviados para {queryset.count()} usuários')
    send_verification_email.short_description = 'Enviar email de verificação'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin para o modelo UserProfile"""
    list_display = ['user', 'followers_count', 'following_count', 
                    'posts_count', 'location']
    list_filter = ['location']
    search_fields = ['user__username', 'user__email', 'bio']
    readonly_fields = ['followers_count', 'following_count', 'posts_count']
    
    fieldsets = (
        ('Informações do Usuário', {
            'fields': ('user',)
        }),
        ('Dados do Perfil', {
            'fields': ('avatar', 'bio', 'location', 'website', 'birth_date')
        }),
        ('Estatísticas', {
            'fields': ('followers_count', 'following_count', 'posts_count'),
            'classes': ('collapse',)
        }),
    )
****************************************************************************************

*Estrutura de Pastas*
text
----------------------------------------------------------------------------------------
project_name/
├── manage.py
├── requirements.txt
├── config/                      # Configurações do projeto
│   ├── __init__.py
│   ├── settings/
│   │   ├── base.py             # Configurações base
│   │   ├── development.py      # Configurações de desenvolvimento
│   │   └── production.py       # Configurações de produção
│   ├── urls.py                 # URLs principais
│   └── wsgi.py
│
├── apps/                        # Todos os apps do sistema
│   ├── __init__.py
│   │
│   ├── accounts/                # App: Autenticação e Perfis
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py            # User, UserProfile
│   │   ├── serializers.py       # Register, Login, Profile
│   │   ├── services.py          # UserService
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── viewsets.py          # AuthViewSet, ProfileViewSet
│   │
│   ├── posts/                    # App: Gerenciamento de Posts
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py            # Post, PostMedia
│   │   ├── serializers.py       # PostSerializer
│   │   ├── services.py          # PostService
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── viewsets.py          # PostViewSet
│   │
│   ├── feed/                     # App: Feed Personalizado
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py            # FeedCache (opcional)
│   │   ├── serializers.py       # FeedSerializer
│   │   ├── services.py          # FeedService (algoritmo)
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── viewsets.py          # FeedViewSet
│   │
│   ├── interactions/             # App: Interações (Likes, Comments)
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py            # Like, Comment, Share
│   │   ├── serializers.py       # CommentSerializer
│   │   ├── services.py          # InteractionService
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── viewsets.py          # CommentViewSet, LikeViewSet
│   │
│   └── social/                   # App: Rede Social (Followers)
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py            # Follow, FollowRequest
│       ├── serializers.py       # FollowSerializer
│       ├── services.py          # SocialService
│       ├── tests.py
│       ├── urls.py
│       └── viewsets.py          # FollowViewSet
│
├── core/                         # Funcionalidades compartilhadas
│   ├── __init__.py
│   ├── authentication.py        # Autenticação personalizada
│   ├── permissions.py           # Permissões customizadas
│   ├── pagination.py            # Paginação padrão
│   ├── exceptions.py            # Tratamento de exceções
│   ├── middleware.py            # Middlewares customizados
│   └── utils.py                 # Funções utilitárias
│
├── media/                        # Arquivos de mídia
│   └── avatars/                 # Avatars dos usuários
│
├── static/                       # Arquivos estáticos
│   └── ...
│
├── logs/                         # Logs do sistema
│   └── app.log
│
├── scripts/                      # Scripts de manutenção
│   ├── populate_db.py           # Popula banco de dados
│   └── backup.py                # Backup do banco
│
├── docs/                         # Documentação
│   └── architecture.md
│
└── README.md
------------------------------------------------------------------------------------

*Fluxo de Exemplo: Criação de Perfil*
- Para ilustrar como os dados fluem através da arquitetura, vamos acompanhar o processo de criação de perfil e upload de avatar.
- Passo a Passo Detalhado
    Cliente faz requisição → POST /api/accounts/profile/upload-avatar/ com token de autenticação
    ViewSet recebe a requisição → ProfileViewSet.upload_avatar()
    ViewSet verifica autenticação → TokenAuthentication valida o token
    ViewSet instancia Serializer → AvatarUploadSerializer(data=request.data)
    Serializer valida os dados:
        Verifica se o arquivo é uma imagem
        Verifica tamanho (máximo 5MB)
        Verifica extensão (jpg, jpeg, png)
    Serializer retorna dados validados → Para o ViewSet
    ViewSet chama Service → UserService.upload_avatar(user, validated_data['avatar'])
    Service valida regras de negócio:
    Verifica tamanho do arquivo
    Verifica extensão do arquivo
    Service processa o avatar:
    Deleta avatar antigo se existir
    Salva novo avatar
    Service atualiza Model → profile.avatar = avatar_file; profile.save()
    Model persiste no banco → Django ORM salva o arquivo e atualiza o registro
    Service retorna → Profile atualizado
    ViewSet formata resposta → Response({'avatar': url, 'message': '...'})
    Cliente recebe resposta → 200 OK com URL do avatar

*Padrões de Nomenclatura*
📂 Apps
Tipo	                    Padrão	    Exemplo
Nome do app	snake_case      (plural)	accounts, posts, interactions
Nome do app	snake_case      (singular)	feed, social

📄 Arquivos
Tipo	    Arquivo	        Exemplo
Modelos	    models.py	    models.py
Serviços	services.py	    services.py
Serializers	serializers.py	serializers.py
Views	    viewsets.py	    viewsets.py
URLs	    urls.py	        urls.py
Admin	    admin.py	    admin.py
Testes	    tests.py	    tests.py

🏷️ Classes
Tipo	        Padrão	        Exemplo
Model	        NomeModelo	    User, UserProfile, Post
Service	        NomeService	    UserService, PostService
Serializer	    NomeSerializer	UserSerializer, RegisterSerializer
ViewSet	        NomeViewSet	    UserViewSet, AuthViewSet
Permission  	NomePermission	IsOwnerOrReadOnly, IsVerifiedUser
Exception	    NomeException	ProfileNotFoundException, InvalidTokenException

📝 Métodos
Tipo        Padrão	        Exemplo
Service     (CRUD)	        get_{model}, create_{model}, update_{model}, delete_{model}
Service     (Ações)	        {action}_{model}	upload_avatar(), send_verification()
ViewSet     (Actions)	    {action}	login(), register(), upload_avatar()
Model       (Propriedades)	is_{state}	is_verified, is_complete_profile
Model       (Ações)	        {action}	increment_followers(), decrement_followers()

📋 URLs
Tipo	    Padrão	                    Exemplo
URL Base	/api/{app_name}/	        /api/accounts/
Action	    /api/{app_name}/{action}/	/api/accounts/auth/login/
Detail	    /api/{app_name}/{id}/	    /api/accounts/profile/1/

/Autenticação e Segurança/
🔐 Token Authentication
- O sistema utiliza Token Authentication do Django REST Framework para garantir segurança em todas as rotas protegidas.

python
****************************************************************************************
# core/authentication.py
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

class CustomTokenAuthentication(TokenAuthentication):
    """
    Autenticação customizada com validação de token
    """
    def authenticate_credentials(self, key):
        try:
            token = self.get_model().objects.select_related('user').get(key=key)
        except self.get_model().DoesNotExist:
            raise AuthenticationFailed('Token inválido')
        
        if not token.user.is_active:
            raise AuthenticationFailed('Usuário inativo')
        
        # Verifica se token expirou (opcional)
        # if token.created < timezone.now() - timedelta(days=7):
        #     raise AuthenticationFailed('Token expirado')
        
        return (token.user, token)
****************************************************************************************

🛡️ Permissões
python
****************************************************************************************
# core/permissions.py
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permissão customizada: apenas o proprietário pode modificar
    """
    def has_object_permission(self, request, view, obj):
        # Permissão de leitura para todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permissão de escrita apenas para o proprietário
        return obj.user == request.user

class IsVerifiedUser(permissions.BasePermission):
    """
    Permissão: apenas usuários verificados podem executar ação
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_verified

class IsProfileOwner(permissions.BasePermission):
    """
    Permissão: apenas o dono do perfil pode modificar
    """
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, User):
            return obj.id == request.user.id
        if hasattr(obj, 'user'):
            return obj.user.id == request.user.id
        return False
****************************************************************************************

📋 Exemplo de Uso
python
****************************************************************************************
# accounts/viewsets.py
from core.permissions import IsVerifiedUser, IsProfileOwner
from core.authentication import CustomTokenAuthentication

class ProfileViewSet(viewsets.GenericViewSet):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsProfileOwner]
    
    def get_permissions(self):
        if self.action == 'upload_avatar':
            permission_classes = [IsVerifiedUser]
        else:
            permission_classes = [IsProfileOwner]
        return [permission() for permission in permission_classes]
        ****************************************************************************************

*Testes*
🧪 Estratégia de Testes
Tipo de Teste	    Ferramenta	            Cobertura
Unit Tests	        Django                  TestCase Models, Services, Serializers
API Tests	        APITestCase	            ViewSets, Endpoints
Integration Tests	TransactionTestCase	    Fluxos completos
Performance Tests	Locust	                Endpoints críticos

✅ Exemplo de Teste de Integração
python
****************************************************************************************
# accounts/tests.py
from django.test import TransactionTestCase
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile

class FullProfileFlowTest(TransactionTestCase):
    """
    Teste de integração: fluxo completo de perfil
    """
    
    def setUp(self):
        self.client = APIClient()
    
    def test_complete_user_flow(self):
        """Teste do fluxo completo: registro → login → perfil → avatar"""
        
        # 1. Registro
        register_data = {
            'username': 'testuser',
            'email': 'test@email.com',
            'password': 'Test@123456',
            'password_confirm': 'Test@123456',
        }
        response = self.client.post('/api/accounts/auth/register/', register_data)
        self.assertEqual(response.status_code, 201)
        token = response.data['token']
        
        # 2. Login
        login_data = {
            'username': 'testuser',
            'password': 'Test@123456'
        }
        response = self.client.post('/api/accounts/auth/login/', login_data)
        self.assertEqual(response.status_code, 200)
        token = response.data['token']
        
        # 3. Configura autenticação
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        
        # 4. Atualiza perfil
        profile_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'bio': 'This is my bio',
            'location': 'São Paulo'
        }
        response = self.client.patch('/api/accounts/profile/update/', profile_data)
        self.assertEqual(response.status_code, 200)
        
        # 5. Upload avatar
        avatar = SimpleUploadedFile(
            name='avatar.jpg',
            content=b'fake_image_content',
            content_type='image/jpeg'
        )
        response = self.client.post(
            '/api/accounts/profile/upload-avatar/',
            {'avatar': avatar},
            format='multipart'
        )
        self.assertEqual(response.status_code, 200)
        
        # 6. Verifica perfil completo
        response = self.client.get('/api/accounts/profile/me/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(response.data['user']['first_name'], 'Test')
        self.assertEqual(response.data['profile']['bio'], 'This is my bio')
        self.assertIsNotNone(response.data['profile']['avatar'])
****************************************************************************************

*Benefícios da Arquitetura*
Benefício	                            Descrição
✅ Separação de Responsabilidades	   Cada componente tem uma função clara e bem definida
✅ Alta Testabilidade	               Services, Models e Serializers são facilmente testáveis
✅ Manutenibilidade	                   Mudanças em uma camada não afetam as outras
✅ Escalabilidade	                   Novos apps podem ser adicionados sem afetar os existentes
✅ Reutilização de Código	           Services podem ser reutilizados em diferentes Views
✅ Segurança	                           Autenticação e permissões centralizadas
✅ Onboarding                           Facilitado Novos desenvolvedores entendem rapidamente a estrutura


*Considerações Finais*
Esta arquitetura foi projetada para garantir a qualidade, segurança e escalabilidade do sistema backend. Ao seguir estas diretrizes, a equipe de desenvolvimento pode trabalhar de forma colaborativa e eficiente, mantendo o código organizado e de fácil manutenção.

🚀 Próximos Passos Sugeridos
Implementar logs estruturados

Adicionar cache (Redis)

Implementar filas (Celery) para tarefas assíncronas

Configurar CI/CD

Adicionar monitoramento com Sentry/Datadog

📚 Referências
Django Documentation: https://docs.djangoproject.com/

Django REST Framework: https://www.django-rest-framework.org/

Clean Architecture: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html

📌 Versão do Documento: 1.0.0
📅 Última Revisão: 16 de Agosto de 2026
✍️ Autor: Lucas Pierroti Penha