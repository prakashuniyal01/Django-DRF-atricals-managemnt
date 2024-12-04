from django.urls import path
from .views import ArticleListCreateView, ArticleRetrieveUpdateDestroyView, CommentView, ReplyView, LikeView,ArticleApprovalView, ArticleSearchView,ArticleDetailView,AdminArticleCRUDView
from django.views.generic import TemplateView

urlpatterns = [
    path('articles/', ArticleListCreateView.as_view(), name='article-list-create'),
     # URL for retrieving, updating, or deleting a specific article
    path('article/<int:pk>/', ArticleDetailView.as_view(), name='article-detail'),
    path('articles/<int:pk>/', ArticleRetrieveUpdateDestroyView.as_view(), name='article-detail'),
    path("articles/<int:article_id>/approve/", ArticleApprovalView.as_view(), name="article-approve"),
    path('articles/search/', ArticleSearchView.as_view(), name='article-search'),
    
    path('articles/<int:article_id>/comments/', CommentView.as_view(), name='comments'),
    path('comments/<int:comment_id>/', CommentView.as_view(), name='comment-detail'),
    path('comments/<int:comment_id>/reply/', ReplyView.as_view(), name='comment-reply'),
    path('comments/<int:comment_id>/like/', LikeView.as_view(), name='comment-like'),
    path('articles/<int:article_id>/like/', LikeView.as_view(), name='article-like'),
    
     # Admin can perform CRUD on all articles
    # path('admins/articles/', AdminArticleCRUDView.as_view(), name='admin-article-crud'),
    # path('admins/articles/<int:pk>/', AdminArticleCRUDView.as_view(), name='admin_article_crud'),
    # path('admins/articles/<int:pk>/', AdminArticleCRUDView.as_view(), name='admin-article-delete'),
    
    # templates rendering 
    path('admins/articles/<int:article_id>/', AdminArticleCRUDView.as_view(), name='admin-article-detail'),
]
