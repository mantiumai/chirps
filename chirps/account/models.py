"""Models for the account appliation."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """Custom profile model for users."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    openai_key = models.CharField(max_length=100, blank=True)


class ProfileInline(admin.StackedInline):
    """Inline admin descriptor for the Profile model."""

    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'


class UserAdmin(BaseUserAdmin):
    """Define a new User admin."""
    inlines = [ProfileInline]


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
