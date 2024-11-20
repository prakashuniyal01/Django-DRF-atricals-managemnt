from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class User(AbstractUser):
    ROLE_CHOICES = [
        ('journalist', 'Journalist'),
        ('editor', 'Editor'),
        ('admin', 'Admin'),
        ('user', 'User'),
    ]

    # Full name field (ensure it is required and not null)
    full_name = models.CharField(max_length=255, null=False, default="Unknown User")

    # Phone number field with validation for the format
    number = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be in the format '+999999999'. Up to 15 digits allowed.",
            )
        ],
        unique=True,
        null=False,
        default="+11234567890"
    )

    # Email is required, and it must be unique
    email = models.EmailField(unique=True)

    # Role with predefined choices
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    # Superuser flag (ensure only one superuser exists)
    is_superuser = models.BooleanField(default=False)

    # Fields that should be required during user creation (excluding username, password)
    REQUIRED_FIELDS = ['email', 'number', 'full_name']

    def save(self, *args, **kwargs):
        # Ensure only one superuser exists in the system
        if self.is_superuser:
            if not self.pk and User.objects.filter(is_superuser=True).exists():
                raise ValueError("Only one superuser is allowed.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name
