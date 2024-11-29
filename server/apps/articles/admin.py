from django.contrib import admin
from .models import Article, Tag, Category, Comment, Like

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Article)    
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'status', 'publish_date']  # Customize which fields to display
    search_fields = ['title', 'author__email']  # Allow search by title and author email
    list_filter = ['status', 'publish_date']  # Filter by status and publish date

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'article', 'content', 'parent', 'edited', 'created_at', 'updated_at']
    search_fields = ['author__email', 'content']  # Allow searching by author email and content
    list_filter = ['edited', 'created_at']  # Enable filtering by edited status and created time
    
    
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'article', 'created_at']  # Customize fields to display
    search_fields = ['user__email', 'article__title']  # Allow searching by user email and article title
    list_filter = ['created_at']  # Enable filtering by creation date

admin.site.register(Article, ArticleAdmin)  # Register the model with custom admin options
admin.site.register(Tag,TagAdmin)  # Register other models like Tag, if necessary
admin.site.register(Category, CategoryAdmin)  # If you have a Category model
admin.site.register(Comment, CommentAdmin)
admin.site.register(Like, LikeAdmin)
