# interactions/serializers.py
from rest_framework import serializers
from .models import Comment
from accounts.serializers import UserDetailSerializer

class CommentSerializer(serializers.ModelSerializer):
    author = UserDetailSerializer(read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    replies_count = serializers.IntegerField(source='replies.count', read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'author', 'author_username', 'post', 
            'parent', 'text', 'likes_count', 'replies_count', 
            'is_liked', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def get_is_liked(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['post', 'parent', 'text']

    def validate(self, attrs):
        parent = attrs.get('parent')
        post = attrs.get('post')
        if parent and parent.post != post:
            raise serializers.ValidationError({"parent": "O comentário pai deve pertencer ao mesmo post."})
        return attrs