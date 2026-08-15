from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

from .serializers import (
    RegisterSerializer, 
    UserDetailSerializer, 
    UpdateProfileSerializer,
    ProfileSerializer
)
from .services import create_user_with_profile

User = get_user_model()


class RegisterView(APIView):
    """Cria o perfil do usuário no sistema"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = create_user_with_profile(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            display_name=serializer.validated_data.get('display_name', '')
        )

        return Response(
            UserDetailSerializer(user).data, 
            status=status.HTTP_201_CREATED
        )


class MeView(APIView):
    """Retorna os dados completos do usuário autenticado."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)


class UpdateProfileView(generics.UpdateAPIView):
    """Atualiza o perfil do usuário logado."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdateProfileSerializer

    def get_object(self):
        return self.request.user.profile