from rest_framework import serializers
from django.contrib.auth import get_user_model
from accounts.serializers import ProfileSerializer

User = get_user_model()

class FollowUserSummarySerializer(serializers.ModelSerializer):
    """
    Retorna o resumo do usuário (útil para listas de seguidores e seguindo).
    """
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'profile']


class FollowToggleResponseSerializer(serializers.Serializer):
    is_following = serializers.BooleanField()
    message = serializers.CharField()