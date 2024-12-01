from rest_framework.permissions import BasePermission
from rest_framework import permissions
class IsAdminOrEditor(permissions.BasePermission):
    """
    Custom permission to only allow access to Admin or Editor users.
    """

    def has_permission(self, request, view):
        # Allow anonymous users to view articles
        if request.method == 'GET':
            return True
        
        # Check if the user is authenticated and has the required role
        if request.user.is_authenticated:
            return request.user.role in ["admin", "editor"]
        
        # If the user is not authenticated, deny access
        return False

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