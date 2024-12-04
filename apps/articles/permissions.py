from rest_framework.permissions import BasePermission
from rest_framework import permissions
from rest_framework import permissions

class IsAdminOrEditor(permissions.BasePermission):
    """
    Custom permission to only allow access to Admin or Editor users.
    """

    def has_permission(self, request, view):
        # Allow all users to view published articles (GET method)
        if request.method == 'GET':
            # Check if the article is published
            if view.kwargs.get('article_status') == 'published':  # Adjust this according to your model logic
                return True
        
        # Check if the user is authenticated and has the required role for non-GET methods (edit, delete, etc.)
        if request.user.is_authenticated:
            return request.user.role in ["admin", "editor"]
        
        return False


class IsAdminOrJournalist(permissions.BasePermission):
    """
    Custom permission to allow only Admins or Journalists.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["admin", "journalist"]


class IsEditorOrAdmin(permissions.BasePermission):
    """
    Allows access to Admins and Editors only.
    """
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role in ["admin", "editor"]
        return False


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of an object to edit or delete it.
    Admin users can modify anything.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_staff
    
class IsAdminOnly(BasePermission):
    """
    Custom permission to allow only Admin users to perform any action.
    """
    def has_permission(self, request, view):
        # Allow GET requests to all authenticated users
        if request.method == 'GET':
            return True
        
        # For all other methods (POST, PUT, DELETE), allow only Admins
        if request.user.is_authenticated:
            return request.user.is_superuser  # Only Admins (is_staff=True) can modify data
        
        return False