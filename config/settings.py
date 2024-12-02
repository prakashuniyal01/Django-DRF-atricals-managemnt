"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import os
from pathlib import Path
from datetime import timedelta
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]

CORS_ALLOW_HEADERS = [
    'content-type',
    'authorization',
    'x-csrftoken',
]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-6o0q*3fd4!*izx&54v)of=-nw#ay-3a5k8^rv-5jgh9ec&-^t4'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

SITE_URL = 'http://172.16.6.94:8000'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'django.contrib.sites',
    'drf_yasg',  # Add drf-yasg for API documentation
    'apps.users',
    'apps.articles',  # Added missing comma
    'cloudinary',
    'cloudinary_storage',
    'corsheaders',
]


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Django REST Framework - Simple JWT configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),  # Access token lifetime (15 minutes)
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),     # Refresh token lifetime (1 day)
    'ROTATE_REFRESH_TOKENS': False,                   # Don't rotate refresh tokens
    'BLACKLIST_AFTER_ROTATION': True,                 # Blacklist refresh tokens after use
}
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # cors middleware     
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates', BASE_DIR / 'dashboard/'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',  # Bcrypt hasher
    'django.contrib.auth.hashers.Argon2PasswordHasher',        # Optional fallback
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',        # Optional fallback
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',    # Optional fallback
]





# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# my local database home 
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # Use MySQL database engine
        'NAME': 'articledb',  # Database name
        'USER': 'root',  # Database username
        'PASSWORD': 'root',  # Database password
        'HOST': 'localhost',  # MySQL database host
        'PORT': '3306',  # MySQL default port
    }
}


# my local database office
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',  # Use MySQL database engine
#         'NAME': 'articlesDBs',  # Database name
#         'USER': 'root',  # Database username
#         'PASSWORD': 'Mobiloitte1',  # Database password
#         'HOST': 'localhost',  # MySQL database host
#         'PORT': '3306',  # MySQL default port
#     }
# }

# Email Backend for development (using console for testing)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Email config 
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # e.g., smtp.gmail.com
EMAIL_PORT = 587  # For TLS
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'maan03saab@gmail.com'
EMAIL_HOST_PASSWORD = 'miow cpse aeom wdmi'
DEFAULT_FROM_EMAIL = 'maan03saab@gmail.com'
# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

AUTH_USER_MODEL = 'users.User'


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

SITE_ID = 1

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Add your Cloudinary credentials
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'article management',
    'API_KEY': '622646197184647',
    'API_SECRET': 'E32aRgeIktXhsmWR7FJ0nK3tGfs',
}

# cloudinary setups 
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# cors hadder 
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite development server
    "http://127.0.0.1:5173", # Alternative localhost
    "http://localhost:8001",  # Vite development server
    "http://127.0.0.1:8001", # Alternative localhost
    "http://localhost:8080",  # Vite development server
    "http://127.0.0.1:8080", # Alternative localhost
]
