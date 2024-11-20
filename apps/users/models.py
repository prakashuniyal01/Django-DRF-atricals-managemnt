from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.db import models
from django.utils.timezone import now
from datetime import timedelta
from .managers import CustomUserManager
import logging

logger = logging.getLogger(__name__)

# User registration model
class User(AbstractUser):
    # Remove the username field
    username = None

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, default="Unknown User")
    number = models.CharField(
        max_length=15,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be in the format '+999999999'. Up to 15 digits allowed.",
            )
        ],
    )

    # Choices for the user role
    ROLE_CHOICES = [
        ('journalist', 'Journalist'),
        ('editor', 'Editor'),
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    # Non-editable field flag for `is_admin_user`
    is_admin_user = models.BooleanField(default=False, editable=True)  # Now editable

    objects = CustomUserManager()  # Assign the custom manager

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'number']

    def save(self, *args, **kwargs):
        try:
            # Check for existing admin user in the database
            if self.role == 'admin' and User.objects.filter(role='admin').exclude(id=self.id).exists():
                raise DRFValidationError("There can only be one admin user.")
            
            # Debugging roles and permissions
            logger.debug(f"Saving user: {self.email} with role: {self.role}")
            logger.debug(f"Before Save - is_staff: {self.is_staff}, is_admin_user: {self.is_admin_user}, is_superuser: {self.is_superuser}")

            # Automatically set `is_staff` for specific roles
            if self.role in ['journalist', 'editor', 'admin']:
                self.is_staff = True
            else:
                self.is_staff = False

            # Automatically set `is_admin_user` based on `is_staff` or `is_superuser`
            self.is_admin_user = self.is_staff or self.is_superuser

            # Ensure `is_superuser` for admin role if required
            if self.role == 'admin':
                self.is_superuser = True
                self.is_staff = True
                self.is_admin_user = True

            logger.debug(f"After Save - is_staff: {self.is_staff}, is_admin_user: {self.is_admin_user}, is_superuser: {self.is_superuser}")

            super().save(*args, **kwargs)

        except DRFValidationError as e:
            # Catch validation error specifically for admin user check
            logger.error(f"Validation error during save: {str(e)}")
            raise e  # Re-raise the exception so the process is aborted

        except Exception as e:
            # Catch any unexpected exceptions and log them
            logger.error(f"Unexpected error during save: {str(e)}")
            raise DRFValidationError(f"An unexpected error occurred while saving the user: {str(e)}")

    def __str__(self):
        return self.full_name


# forget otp auth 
class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        """Check if the OTP is still valid (within 10 minutes)."""
        try:
            return now() < self.created_at + timedelta(minutes=10)
        except Exception as e:
            raise ValueError(f"Error checking OTP validity: {str(e)}")