# admin.py
from django.contrib import admin
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'created_at']
    list_filter = ['status', 'author', 'category']

# @admin.register(Comment)
# class CommentAdmin(admin.ModelAdmin):
#     list_display = ['article', 'user', 'content', 'created_at']

# admin.site.register(Tag)
# admin.site.register(Category)
