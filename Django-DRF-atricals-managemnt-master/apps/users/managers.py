from django.contrib.auth.base_user import BaseUserManager
import logging

logger = logging.getLogger(__name__)

        
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with the given email and password.
        """
        try:
            if not email:
                raise ValueError("The Email field must be set")
            
            # Normalize the email
            email = self.normalize_email(email)
            extra_fields.setdefault('is_staff', False)
            extra_fields.setdefault('is_superuser', False)
            
            # Create the user instance
            user = self.model(email=email, **extra_fields)
            user.set_password(password)
            
            # Save the user to the database
            user.save(using=self._db)
            
            logger.debug(f"User created successfully: {user.email}, Role: {user.role}")
            return user

        except ValueError as e:
            logger.error(f"Error during user creation: {str(e)}")
            raise e  # Re-raise the exception after logging it

        except Exception as e:
            logger.error(f"Unexpected error during user creation: {str(e)}")
            raise ValueError(f"An unexpected error occurred while creating the user: {str(e)}")

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with the given email and password.
        """
        try:
            extra_fields.setdefault('is_staff', True)
            extra_fields.setdefault('is_superuser', True)
            extra_fields.setdefault('is_active', True)

            if extra_fields.get('is_staff') is not True:
                raise ValueError("Superuser must have is_staff=True.")
            if extra_fields.get('is_superuser') is not True:
                raise ValueError("Superuser must have is_superuser=True.")
            
            # Call the create_user method to create the superuser
            user = self.create_user(email, password, **extra_fields)
            logger.debug(f"Superuser created successfully: {user.email}")
            return user

        except ValueError as e:
            logger.error(f"Error during superuser creation: {str(e)}")
            raise e  # Re-raise the exception after logging it

        except Exception as e:
            logger.error(f"Unexpected error during superuser creation: {str(e)}")
            raise ValueError(f"An unexpected error occurred while creating the superuser: {str(e)}")
