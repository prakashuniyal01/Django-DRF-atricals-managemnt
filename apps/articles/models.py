from django.db import models
from django.conf import settings

class Article(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('rejected', 'Rejected'),
    ]

    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='articles'
    )  # Reference to User model; email will be retrieved via this relationship
    image_url = models.URLField(blank=True, null=True)  # Store Cloudinary image URL
    tags = models.JSONField(default=list, blank=True)  # Use a list for tags
    category = models.CharField(max_length=100)  # Assuming categories are predefined strings
    publish_date = models.DateField()  # Ensure validation for future dates is applied in serializer
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
