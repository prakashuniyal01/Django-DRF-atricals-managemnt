from django.urls import path
from .views import ArticleListCreateView, ArticleRetrieveUpdateDestroyView

urlpatterns = [
    # Unified endpoint for listing and creating articles
    path('articles/', ArticleListCreateView.as_view(), name='article-list-create'),
    
    # Unified endpoint for retrieving, updating, and deleting a specific article
    path('articles/<int:pk>/', ArticleRetrieveUpdateDestroyView.as_view(), name='article-detail'),
]
    