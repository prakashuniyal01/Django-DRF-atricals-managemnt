from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from .models import User

class CustomAdminSite(AdminSite):
    def has_permission(self, request):
        # Allow access only for users with 'admin' role
        if request.user.is_authenticated and request.user.role == 'admin':
            return True
        return False

# Register the custom admin site
admin_site = CustomAdminSite(name='custom_admin')

class CustomUserAdmin(DefaultUserAdmin):
    list_display = ('email', 'full_name', 'number', 'role', 'is_staff', 'is_superuser', 'is_admin_user', 'is_active')
    list_filter = ('role', 'is_staff', 'is_admin_user', 'is_superuser', 'is_active')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('full_name', 'number', 'role')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_admin_user', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'full_name', 'number', 'role', 'is_active', 'is_staff', 'is_admin_user'),
        }),
    )

    search_fields = ('email', 'full_name', 'number')
    ordering = ('email',)

# Register the custom admin
admin_site.register(User, CustomUserAdmin)

# Use the custom admin site instead of the default one
admin.site = admin_site
