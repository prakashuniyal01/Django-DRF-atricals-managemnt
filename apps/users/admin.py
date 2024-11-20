from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'number', 'full_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'is_superuser')
    search_fields = ('username', 'email', 'number')
    ordering = ('email',)

admin.site.register(User, CustomUserAdmin)
