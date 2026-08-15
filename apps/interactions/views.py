# interactions/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError

from .models import Comment
from .serializers import CommentSerializer, CommentCreateSerializer
from .permissions import IsAuthorOrReadOnly
from .services import CommentService, LikeService

class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        try:
            comment = CommentService.create_comment(
                user=self.request.user,
                post_id=serializer.validated_data['post'].id,
                text=serializer.validated_data['text'],
                parent_id=serializer.validated_data.get('parent').id if serializer.validated_data.get('parent') else None
            )
            serializer.instance = comment
        except ValidationError as e:
            raise serializers.ValidationError(e.message)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        """Toggle de curtida no comentário"""
        try:
            is_liked = LikeService.toggle_comment_like(user=request.user, comment_id=pk)
            status_str = "curtido" if is_liked else "descurtido"
            return Response({"detail": f"Comentário {status_str} com sucesso.", "is_liked": is_liked}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def get_queryset(self):
        queryset = Comment.objects.select_related('author', 'post').prefetch_related('likes', 'replies').all()
        post_id = self.request.query_params.get('post')
        if post_id is not None:
            queryset = queryset.filter(post_id=post_id)
        return queryset


class PostLikeView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, post_id=None):
        """Toggle de curtida no post"""
        try:
            is_liked = LikeService.toggle_post_like(user=request.user, post_id=post_id)
            status_str = "curtido" if is_liked else "descurtido"
            return Response({"detail": f"Post {status_str} com sucesso.", "is_liked": is_liked}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)