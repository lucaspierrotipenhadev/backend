from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

from .models import Post
from .permissions import IsAuthorOrReadOnly
from .serializers import PostSerializer, PostUpdateSerializer
from .services import create_post_with_media, update_post


class PostListCreateView(generics.ListCreateAPIView):
    """
    GET: Lista todos os posts cadastrados (ordem decrescente por data).
    POST: Cria um novo post e aceita mídias opcionais.
    """
    queryset = Post.objects.all().prefetch_related('medias', 'author__profile')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        files = self.request.FILES.getlist('files')
        post = create_post_with_media(
            author=self.request.user,
            text=serializer.validated_data['text'],
            files=files
        )
        return post

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = self.perform_create(serializer)
        return Response(
            PostSerializer(post, context={'request': request}).data, 
            status=status.HTTP_201_CREATED
        )


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Exibe detalhes de um post específico.
    PUT/PATCH: Edita o texto do post (Somente o autor).
    DELETE: Apaga o post (Somente o autor).
    """
    queryset = Post.objects.all().prefetch_related('medias', 'author__profile')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PostUpdateSerializer
        return PostSerializer

    def perform_update(self, serializer):
        post = update_post(
            post=self.get_object(),
            text=serializer.validated_data.get('text', self.get_object().text)
        )
        return post

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        updated_instance = self.perform_update(serializer)
        
        return Response(
            PostSerializer(updated_instance, context={'request': request}).data
        )