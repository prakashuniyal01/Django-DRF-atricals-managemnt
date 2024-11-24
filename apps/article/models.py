from django.db import models
from django.utils.timezone import now
from django.conf import settings


class Category(models.Model):
    """
    Represents an article category.
    """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    Represents a tag that can be assigned to articles.
    """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    """
    Represents an article in the system.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, null=True, blank=True)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='articles'
    )
    image_url = models.URLField(null=True, blank=True)
    publish_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='draft'
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviewed_articles'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    categories = models.ManyToManyField(
        'Category', 
        related_name='articles'
    )  # ManyToManyField for multiple categories
    tags = models.ManyToManyField(
        'Tag', 
        related_name='articles'
    )
    deleted_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Custom save logic:
        - Automatically set `approved_at` if the status is published.
        """
        if self.status == 'published' and not self.approved_at:
            self.approved_at = now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        """
        Additional metadata for the Article model.
        """
        ordering = ['-created_at']  # Order by latest created articles by default
