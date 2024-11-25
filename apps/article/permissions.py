from rest_framework.permissions import BasePermission

class IsAdminOrJournalist(BasePermission):
    """
    Custom permission to allow only Admins or Journalists.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["admin", "journalist"]


class IsEditorOrAdmin(BasePermission):
    """
    Allows access to Admins and Editors only.
    """
    def has_permission(self, request, view):
        return request.user.role in ["admin", "editor"]