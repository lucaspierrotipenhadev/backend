from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Permite leitura para qualquer usuário (autenticado ou não), 
    mas escrita apenas para o autor do objeto.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user