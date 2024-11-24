from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from .models import Article
from .serializers import ArticleSerializer, ArticleCreateUpdateSerializer
from .permissions import IsAdminOrJournalist

class ArticleListCreateView(generics.ListCreateAPIView):
    """
    Unified view for listing and creating articles for Admins and Journalists.
    """
    serializer_class = ArticleCreateUpdateSerializer
    permission_classes = [IsAdminOrJournalist]

    def get_queryset(self):
        """
        Admins can view all articles, while Journalists can only view their own articles.
        """
        user = self.request.user
        if user.role == "admin":
            return Article.objects.all()
        elif user.role == "journalist":
            return Article.objects.filter(author=user)
        else:
            raise PermissionDenied("You do not have permission to view articles.")

    def perform_create(self, serializer):
        """
        Admins and Journalists can create articles, but only Admins can set status to 'published'.
        """
        user = self.request.user
        if user.role not in ["admin", "journalist"]:
            raise PermissionDenied("You do not have permission to create articles.")
        article = serializer.save(author=user)
        if user.role == "journalist" and article.status == "published":
            raise PermissionDenied("Journalists cannot directly publish articles.")
        article.save()


class ArticleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Unified view for retrieving, updating, and deleting articles for Admins and Journalists.
    """
    serializer_class = ArticleCreateUpdateSerializer
    permission_classes = [IsAdminOrJournalist]

    def get_queryset(self):
        """
        Admins can access all articles, while Journalists can access their own articles only.
        """
        user = self.request.user
        if user.role == "admin":
            return Article.objects.all()
        elif user.role == "journalist":
            return Article.objects.filter(author=user)
        else:
            raise PermissionDenied("You do not have permission to access this article.")

    def perform_update(self, serializer):
        """
        Admins can update all articles, while Journalists can update their own articles with restrictions.
        """
        user = self.request.user
        article = self.get_object()

        if user.role == "journalist" and article.author != user:
            raise PermissionDenied("You can only edit your own articles.")
        if user.role == "journalist" and serializer.validated_data.get("status") == "published":
            raise PermissionDenied("Journalists cannot directly publish articles.")
        
        serializer.save()

    def perform_destroy(self, instance):
        """
        Admins can delete all articles, while Journalists can delete their own unpublished articles.
        """
        user = self.request.user

        if user.role == "journalist":
            if instance.author != user:
                raise PermissionDenied("You can only delete your own articles.")
            if instance.status == "published":
                raise PermissionDenied("You cannot delete published articles.")

        instance.delete()
