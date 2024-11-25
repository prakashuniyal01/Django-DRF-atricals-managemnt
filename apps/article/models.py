from django.db import models
from django.utils.timezone import now
from django.conf import settings

User = settings.AUTH_USER_MODEL
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
        # settings.AUTH_USER_MODEL, 
        User,
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='articles'
    )
    image_url = models.URLField(null=True, blank=True)
    publish_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='draft'
    )
    reviewed_by = models.ForeignKey(
        # settings.AUTH_USER_MODEL, 
        User,
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviewed_articles'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    categories = models.ManyToManyField(
        'Category', 
        related_name='articles'
    )
    tags = models.ManyToManyField(
        'Tag', 
        related_name='articles'
    )
    deleted_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Automatically set `approved_at` if the status is 'published'.
        """
        if self.status == 'published' and not self.approved_at:
            self.approved_at = now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']



class Comment(models.Model):
    article = models.ForeignKey(Article, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name="replies", on_delete=models.CASCADE)
    edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.article}"
    
class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes")
    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name="likes")
    comment = models.ForeignKey('Comment', null=True, blank=True, on_delete=models.CASCADE, related_name="likes")  # New comment field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.comment:
            return f"Like by {self.user} on Comment {self.comment.id}"
        return f"Like by {self.user} on Article {self.article.id}"

    class Meta:
        # If 'comment' is provided, ensure a user can only like a specific comment or article once.
        unique_together = ('user', 'article', 'comment')  # One like per user per article/comment
        # You could adjust the constraint as per your requirements, e.g., if likes are allowed only on articles
        # unique_together = ('user', 'article')
