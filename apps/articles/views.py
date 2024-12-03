from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Comment, Like, Article,Category, Tag
from .serializers import ArticleSerializer, ArticleCreateUpdateSerializer, CommentSerializer, LikeSerializer,ArticleSearchSerializer
from .permissions import IsAdminOrJournalist, IsEditorOrAdmin, IsAdminOrEditor, IsAuthorOrReadOnly
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.db import IntegrityError
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
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
    """
    API view for creating, listing, updating, and deleting comments.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get(self, request, article_id):
        try:
            comments = Comment.objects.filter(article_id=article_id, parent=None).prefetch_related('likes')
            serializer = CommentSerializer(comments, many=True)
            
            # Include total likes and replies for each comment
            for comment_data in serializer.data:
                comment = Comment.objects.get(id=comment_data['id'])
                comment_data['likes_count'] = Like.objects.filter(comment=comment).count()
                
                # Fetch replies for the comment and include author details
                replies = Comment.objects.filter(parent=comment).prefetch_related('likes')
                reply_data = []
                for reply in replies:
                    reply_info = {
                        'id': reply.id,
                        'author': reply.author.username,  # Assuming `username` is used for user identification
                        'content': reply.content,
                        'likes_count': Like.objects.filter(comment=reply).count(),
                    }
                    reply_data.append(reply_info)
                comment_data['replies'] = reply_data

            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, article_id):
        try:
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(article_id=article_id, author=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, comment_id):
        try:
            comment = Comment.objects.get(id=comment_id)
            self.check_object_permissions(request, comment)
            serializer = CommentSerializer(comment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({"error": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, comment_id):
        try:
            comment = Comment.objects.get(id=comment_id)
            self.check_object_permissions(request, comment)
            comment.delete()
            return Response({"detail": "Comment deleted."}, status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response({"error": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class ReplyView(APIView):
    """
    API view for adding replies to comments.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, comment_id):
        try:
            parent_comment = Comment.objects.get(id=comment_id)
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(article=parent_comment.article, parent=parent_comment, author=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({"error": "Parent comment not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LikeView(APIView):
    """
    API view for liking and unliking articles or comments.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, comment_id=None, article_id=None):
        try:
            if comment_id:
                comment = Comment.objects.get(id=comment_id)
                if Like.objects.filter(user=request.user, comment=comment).exists():
                    return Response({"detail": "Already liked this comment."}, status=status.HTTP_400_BAD_REQUEST)

                Like.objects.create(user=request.user, comment=comment)
                likes_count = Like.objects.filter(comment=comment).count()
                return Response({"detail": "Comment liked.", "likes_count": likes_count}, status=status.HTTP_201_CREATED)

            if article_id:
                article = Article.objects.get(id=article_id)
                if Like.objects.filter(user=request.user, article=article).exists():
                    return Response({"detail": "Already liked this article."}, status=status.HTTP_400_BAD_REQUEST)

                Like.objects.create(user=request.user, article=article)
                likes_count = Like.objects.filter(article=article).count()
                return Response({"detail": "Article liked.", "likes_count": likes_count}, status=status.HTTP_201_CREATED)
        except ObjectDoesNotExist:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, comment_id=None, article_id=None):
        try:
            if comment_id:
                comment = Comment.objects.get(id=comment_id)
                like = Like.objects.filter(user=request.user, comment=comment)
                if like.exists():
                    like.delete()
                    likes_count = Like.objects.filter(comment=comment).count()
                    return Response({"detail": "Comment unliked.", "likes_count": likes_count}, status=status.HTTP_204_NO_CONTENT)
                return Response({"detail": "Like not found."}, status=status.HTTP_404_NOT_FOUND)

            if article_id:
                article = Article.objects.get(id=article_id)
                like = Like.objects.filter(user=request.user, article=article)
                if like.exists():
                    like.delete()
                    likes_count = Like.objects.filter(article=article).count()
                    return Response({"detail": "Article unliked.", "likes_count": likes_count}, status=status.HTTP_204_NO_CONTENT)
                return Response({"detail": "Like not found."}, status=status.HTTP_404_NOT_FOUND)
        except ObjectDoesNotExist:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)       
            

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