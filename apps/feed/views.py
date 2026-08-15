# apps/social/views.py
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination

from .services import FeedService
from .serializers import FeedPostSerializer
from .permissions import IsAuthenticatedForFeed


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class FeedView(generics.ListAPIView):
    """
    GET /api/feed/feed/
    Retorna a linha do tempo (feed) do usuário autenticado.
    """
    permission_classes = [IsAuthenticatedForFeed]
    serializer_class = FeedPostSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return FeedService.get_user_feed(user=self.request.user)