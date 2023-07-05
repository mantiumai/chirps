"""Models for the account appliation."""
from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """Custom profile model for users."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    openai_key = models.CharField(max_length=100, blank=True)
