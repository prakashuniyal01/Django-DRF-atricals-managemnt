# permissions.py
from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Admin role ke liye permission class.
    """
    def has_permission(self, request, view):
        return request.user.role == 'Admin'

class IsEditor(permissions.BasePermission):
    """
    Editor role ke liye permission class.
    """
    def has_permission(self, request, view):
        return request.user.role == 'Editor'

class IsJournalist(permissions.BasePermission):
    """
    Journalist role ke liye permission class.
    """
    def has_permission(self, request, view):
        return request.user.role == 'Journalist'

class IsUser(permissions.BasePermission):
    """
    General User role ke liye permission class.
    """
    def has_permission(self, request, view):
        return request.user.role == 'User'
