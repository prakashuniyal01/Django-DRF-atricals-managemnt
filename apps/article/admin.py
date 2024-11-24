# from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from .models import Article, Tag, Category


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """
    Custom admin configuration for the Article model.
    """
    list_display = ('title', 'author', 'status', 'publish_date')
    list_filter = ('status', 'publish_date', 'categories')  # 'categories' is ManyToManyField
    search_fields = ('title', 'content')
    filter_horizontal = ('tags', 'categories')  # Enables selection of ManyToMany fields

    def get_queryset(self, request):
        """
        Override the queryset to handle filtering or annotations, if needed.
        """
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('tags', 'categories')  # Optimize for related fields


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Custom admin configuration for the Tag model.
    """
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Custom admin configuration for the Category model.
    """
    list_display = ('name',)
    search_fields = ('name',)


# No need to call `admin.site.register` again for these models
admin.site.register(Article)
admin.site.register(Tag)
admin.site.register(Category)
