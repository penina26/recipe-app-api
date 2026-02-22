"""
Django admin customization.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# 1. Import Django's built-in forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from core import models


# 2. Create custom forms to handle the passwords securely
class CustomUserCreationForm(UserCreationForm):
    """Form for creating a new user with password confirmation."""
    class Meta(UserCreationForm.Meta):
        model = models.User
        fields = ('email', 'name', 'is_active', 'is_staff', 'is_superuser')

class CustomUserChangeForm(UserChangeForm):
    """Form for updating users."""
    class Meta:
        model = models.User
        fields = ('email', 'name', 'is_active', 'is_staff', 'is_superuser')


# 3. Update  UserAdmin
class UserAdmin(BaseUserAdmin): 
    """Define the admin pages for users."""

    # Tell the Admin panel to use django custom forms!
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    ordering = ['id']
    list_display = ['email', 'name']

    # Override fieldsets for the "Edit User" page
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        ('Important dates', {'fields': ('last_login',)}),
    )

    # Override add_fieldsets for the "Add User" creation page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            # 4. Use 'password1' and 'password2' - these are the internal names 
            #    UserCreationForm uses to render the two confirmation boxes.
            'fields': ('email', 'password1', 'password2', 'name', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )
    
    search_fields = ['email']
    readonly_fields = ['last_login']


admin.site.register(models.User, UserAdmin)

admin.site.register(models.Recipe)