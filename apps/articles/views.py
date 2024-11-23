from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ArticleSerializer
from django.core.exceptions import ValidationError

class ArticleCreateView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Assign the authenticated user as the author
            data = request.data.copy()
            data['author'] = request.user.id  # Use the primary key of the authenticated user
            
            serializer = ArticleSerializer(data=data)
            if serializer.is_valid():
                serializer.save(author=request.user)  # Explicitly set the author
                return Response({"message": "Article created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An unexpected error occurred", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
