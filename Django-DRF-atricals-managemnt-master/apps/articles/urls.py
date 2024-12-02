from django.urls import path
from .views import ArticleListCreateView, ArticleRetrieveUpdateDestroyView, CommentView, ReplyView, LikeView,ArticleApprovalView
from django.views.generic import TemplateView

urlpatterns = [
    path('articles/', ArticleListCreateView.as_view(), name='article-list-create'),
    path('articles/<int:pk>/', ArticleRetrieveUpdateDestroyView.as_view(), name='article-detail'),
    path('articles/<int:article_id>/comments/', CommentView.as_view(), name='comments'),
    path('comments/<int:comment_id>/', CommentView.as_view(), name='comment-detail'),
    path('comments/<int:comment_id>/reply/', ReplyView.as_view(), name='comment-reply'),
    path('comments/<int:comment_id>/like/', LikeView.as_view(), name='comment-like'),
    path("articles/<int:article_id>/approve/", ArticleApprovalView.as_view(), name="article-approve"),
    
    
    # templates rendering 
     path('article-page/<int:pk>/', TemplateView.as_view(template_name='article_detail.html'), name='article-detail')
]
