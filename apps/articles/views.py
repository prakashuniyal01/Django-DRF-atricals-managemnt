from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Comment, Like, Article,Category, Tag
from .serializers import ArticleSerializer, ArticleCreateUpdateSerializer, CommentSerializer, LikeSerializer,ArticleSearchSerializer
from .permissions import IsAdminOrJournalist, IsEditorOrAdmin, IsAdminOrEditor
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.db import IntegrityError
from django.db.models import Q
from rest_framework.exceptions import ValidationError


class ArticleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAdminOrEditor] 

class ArticleListCreateView(generics.ListCreateAPIView):
    """
    View for listing all articles (publicly accessible) and creating articles (restricted to Admins and Journalists).
    """
    def get_permissions(self):
        """
        Override permissions:
        - Allow any user to GET (list).
        - Restrict POST to authenticated Admins and Journalists.
        """
        if self.request.method == "GET":
            return [AllowAny()]  # Public users can only view published articles
        return [IsAdminOrJournalist()]  # Admins and Journalists can create articles

    def get_queryset(self):
        """
        Return appropriate articles based on user role:
        - Admins can see all articles (published and unpublished).
        - Journalists can only see their own articles.
        - Public users can only see published articles.
        """
        if self.request.user.is_authenticated:
            user = self.request.user

            if self.request.method == "GET":
                if user.role == "admin":
                    return Article.objects.all()  # Admin can see all articles, regardless of status
                elif user.role == "editor":
                    return Article.objects.all()  # Editor can see all articles
                elif user.role == "journalist":
                    return Article.objects.filter(author=user)  # Journalists can only see their own articles
                else:
                    return Article.objects.filter(status="published")  # For other authenticated users, only show published articles

        # If the user is not authenticated, show only published articles
        return Article.objects.filter(status="published")

    def get_serializer_class(self):
        """
        Use appropriate serializer for list or create operations.
        """
        if self.request.method == "POST":
            return ArticleCreateUpdateSerializer
        return ArticleSerializer

    def perform_create(self, serializer):
        """
        Restrict article creation to Admins and Journalists.
        """
        if not self.request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to create an article.")
        user = self.request.user
        if user.role not in ["admin", "journalist"]:
            raise PermissionDenied("You do not have permission to create articles.")
        serializer.save(author=user)


class ArticleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for retrieving articles (publicly accessible) and updating/deleting articles (restricted to Admins, Journalists, and Editors).
    """
    def get_permissions(self):
        """
        Override permissions:
        - Allow any user to GET (retrieve).
        - Restrict PUT, PATCH, DELETE to authenticated Admins, Journalists, and Editors.
        """
        if self.request.method == "GET":
            return [AllowAny()]  # Public users can only retrieve published articles
        return [IsEditorOrAdmin()]  # Admins, Editors can perform update/delete actions

    def get_queryset(self):
        """
        Return appropriate articles based on user role:
        - Admins can see all articles (published and unpublished).
        - Journalists can only see their own articles.
        - Editors can see draft/pending articles as well.
        - Public users can only view published articles.
        """
        if self.request.user.is_authenticated:
            user = self.request.user

            if self.request.method == "GET":
                if user.role == "admin":
                    return Article.objects.all()  # Admin can see all articles
                elif user.role == "editor":
                    return Article.objects.all()  # Editors can see all articles
                elif user.role == "journalist":
                    return Article.objects.filter(author=user)  # Journalists can only see their own articles
                else:
                    return Article.objects.filter(status="published")  # Default for public users is only published articles

        return Article.objects.filter(status="published")  # Default for unauthenticated users is only published articles

    def get_serializer_class(self):
        """
        Use appropriate serializer for retrieve, update, or delete operations.
        """
        if self.request.method in ["PUT", "PATCH"]:
            return ArticleCreateUpdateSerializer
        return ArticleSerializer

    def perform_update(self, serializer):
        """
        Restrict update permissions:
        - Journalists can only update their own articles, excluding 'published' status.
        - Admins and Editors can update any article.
        """
        user = self.request.user
        article = self.get_object()

        # Admin logic: can update any article
        if user.role == "admin":
            serializer.save()
            return

        # Journalist restrictions: Can only edit their own articles
        if user.role == "journalist":
            if article.author != user:
                raise PermissionDenied("You can only edit your own articles.")
            if serializer.validated_data.get("status") == "published":
                raise PermissionDenied("Journalists cannot directly publish articles.")

        # Editor logic: Editors can approve, reject, publish, or edit
        if user.role == "editor":
            # Editors cannot modify their own articles
            if article.author == user:
                raise PermissionDenied("Editors cannot modify their own articles.")

            # Editors can only update certain fields like status and content
            allowed_fields = {"status", "content"}
            invalid_fields = set(serializer.validated_data.keys()) - allowed_fields
            if invalid_fields:
                raise PermissionDenied(
                    f"Editors can only update the following fields: {', '.join(allowed_fields)}."
                )

        # Save the article, for Editors we also set the reviewed_by field
        serializer.save(reviewed_by=user)

    def perform_destroy(self, instance):
        """
        Restrict delete permissions:
        - Journalists can only delete their own unpublished articles.
        - Admins can delete any article.
        - Editors cannot delete articles.
        """
        user = self.request.user

        if user.role == "journalist":
            if instance.author != user:
                raise PermissionDenied("You can only delete your own articles.")
            if instance.status == "published":
                raise PermissionDenied("You cannot delete published articles.")

        elif user.role == "editor":
            raise PermissionDenied("Editors cannot delete articles.")  # Editors cannot delete

        instance.delete()


class CommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, article_id):
        try:
            article = get_object_or_404(Article, id=article_id)
            
            # Ensure 'author' and 'article' are set
            data = request.data.copy()
            data['author'] = request.user.id  # Use authenticated user's ID as the author
            data['article'] = article.id     # Associate the comment with the article

            # Serialize and validate the data
            serializer = CommentSerializer(data=data)
            if serializer.is_valid():
                serializer.save(author=request.user)  # Explicitly set the author
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "error": "An unexpected error occurred while adding the comment.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def patch(self, request, comment_id):
        try:
            comment = get_object_or_404(Comment, id=comment_id, author=request.user)
            serializer = CommentSerializer(comment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(edited=True)  # Mark the comment as edited
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "error": "An unexpected error occurred while updating the comment.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, comment_id):
        try:
            comment = get_object_or_404(Comment, id=comment_id, author=request.user)
            comment.delete()
            return Response({"message": "Comment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                "error": "An unexpected error occurred while deleting the comment.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id):
        try:
            parent_comment = get_object_or_404(Comment, id=comment_id)
            data = request.data.copy()
            data['author'] = request.user.id
            data['article'] = parent_comment.article.id
            data['parent'] = parent_comment.id

            serializer = CommentSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "error": "An unexpected error occurred while adding the reply.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id):
        try:
            comment = get_object_or_404(Comment, id=comment_id)
            like, created = Like.objects.get_or_create(comment=comment, user=request.user)
            if created:
                return Response({"message": "Comment liked successfully"}, status=status.HTTP_201_CREATED)
            return Response({"message": "You already liked this comment"}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response({
                "error": "You have already liked this comment."
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "error": "An unexpected error occurred while liking the comment.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, comment_id):
        try:
            comment = get_object_or_404(Comment, id=comment_id)
            like = get_object_or_404(Like, comment=comment, user=request.user)
            like.delete()
            return Response({"message": "Like removed successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                "error": "An unexpected error occurred while removing the like.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            

class ArticleApprovalView(APIView):
    """
    APIView for Editors to approve or reject articles.
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def patch(self, request, article_id):
        try:
            # Get the article object
            article = get_object_or_404(Article, id=article_id)

            # Check if the user is an editor
            if request.user.role != "editor":
                raise PermissionDenied("You do not have permission to approve or publish articles.")

            # Update the status to 'approved', 'rejected', or 'published'
            new_status = request.data.get("status")  # Use a different name here
            if new_status not in ["approved", "rejected", "published"]:
                return Response(
                    {"error": "Invalid status. Only 'approved', 'rejected', or 'published' are allowed."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Editors can change the status to 'approved', 'rejected', or 'published'
            if new_status == "published" and article.status != "approved":
                return Response(
                    {"error": "You can only publish articles that have been approved."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            article.status = new_status
            article.reviewed_by = request.user  # Track the reviewer (editor)
            article.save()

            return Response(
                {"message": f"Article has been {new_status} successfully."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "error": "An unexpected error occurred while processing the request.",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# serach
class ArticleSearchView(APIView):
    """
    API to search published articles by category or tag.
    """

    def get(self, request, *args, **kwargs):
        try:
            # Extract query parameters
            categories = request.GET.get("categories", "")
            tags = request.GET.get("tags", "")

            # Split and clean categories and tags input
            category_terms = [term.strip() for term in categories.split(",") if term.strip()]
            tag_terms = [term.strip() for term in tags.split(",") if term.strip()]

            # Validate input: at least one category or tag must be provided
            if not category_terms and not tag_terms:
                raise ValidationError("At least one category or tag is required to perform the search.")

            # Query only published articles (exclude drafts)
            query_filter = Article.objects.filter(status="published")

            # Query articles by categories first
            if category_terms:
                query_filter = query_filter.filter(categories__name__in=category_terms)

            # If no articles are found by category, fallback to tags
            if not query_filter.exists() and tag_terms:
                query_filter = Article.objects.filter(tags__name__in=tag_terms, status="published")

            # If still no articles found, return empty response
            if not query_filter.exists():
                return Response([], status=status.HTTP_200_OK)

            # Serialize the articles
            serializer = ArticleSerializer(query_filter.distinct(), many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)