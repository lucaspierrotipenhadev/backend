from rest_framework import serializers
from accounts.serializers import UserDetailSerializer
from .models import Post, PostMedia


class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ['id', 'file', 'media_type', 'created_at']
        read_only_fields = ['id', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    author = UserDetailSerializer(read_only=True)
    medias = PostMediaSerializer(many=True, read_only=True)
    
    # Campo auxiliar para receber múltiplos arquivos na criação/upload
    files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Post
        fields = ['id', 'author', 'text', 'edited', 'medias', 'files', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'edited', 'created_at', 'updated_at']


class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['text']