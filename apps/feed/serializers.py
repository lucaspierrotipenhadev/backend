# apps/social/serializers.py
from rest_framework import serializers
from posts.models import Post, PostMedia
from accounts.serializers import UserDetailSerializer


class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ['id', 'file', 'media_type', 'created_at']


class FeedPostSerializer(serializers.ModelSerializer):
    author = UserDetailSerializer(read_only=True)
    media = PostMediaSerializer(source='medias', many=True, read_only=True)
    
    # Campos anotados dinamicamente via FeedService
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    has_liked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 
            'author', 
            'text', 
            'media', 
            'edited', 
            'created_at', 
            'updated_at',
            'likes_count',
            'comments_count',
            'has_liked',
        ]