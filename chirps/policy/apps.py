"""Configuration options for the policy application."""
from django.apps import AppConfig


class PolicyConfig(AppConfig):
    """Configuration options for the policy application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'policy'
