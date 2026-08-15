# apps/social/permissions.py
from rest_framework import permissions


class IsAuthenticatedForFeed(permissions.BasePermission):
    """
    Garante acesso apenas para usuários autenticados no feed.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)