from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from .services import FollowService
from .serializers import FollowUserSummarySerializer, FollowToggleResponseSerializer
from .models import FollowUser

User = get_user_model()

class ToggleFollowView(APIView):
    """
    POST /api/social/users/<id>/follow/
    Seguir / Deixar de seguir um usuário.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        try:
            is_following = FollowService.toggle_follow(
                follower=request.user, 
                following_id=user_id
            )
            msg = "Usuário seguido com sucesso." if is_following else "Você deixou de seguir este usuário."
            
            return Response(
                {"is_following": is_following, "message": msg}, 
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)


class FollowersListView(generics.ListAPIView):
    """
    GET /api/social/users/<id>/followers/
    Lista todos os usuários que SEGUEM o usuário especificado.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FollowUserSummarySerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        # Pega os usuários cujos relacionamentos apontam para este 'following'
        return User.objects.filter(following_relationships__following=user).select_related('profile')


class FollowingListView(generics.ListAPIView):
    """
    GET /api/social/users/<id>/following/
    Lista todos os usuários que o usuário especificado ESTÁ SEGUINDO.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FollowUserSummarySerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        # Pega os usuários onde este usuário é o 'follower'
        return User.objects.filter(follower_relationships__follower=user).select_related('profile')