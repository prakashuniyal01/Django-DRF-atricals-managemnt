from rest_framework.permissions import BasePermission

class IsAdminOrJournalist(BasePermission):
    """
    Custom permission to grant access only to Admins and Journalists.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'journalist']
