from rest_framework.permissions import BasePermission

class IsJournalistOrAdmin(BasePermission):
    """
    Custom permission to allow only journalists or admins to access certain views.
    """

    def has_permission(self, request, view):
        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            print("Permission denied: User is not authenticated.")
            return False
        
        # Check if the user's role is journalist or admin
        if request.user.role in ['journalist', 'admin']:
            return True
        
        # Log details for debugging
        print(f"Permission denied for user {request.user.username} with role {request.user.role}")
        return False
