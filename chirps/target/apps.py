"""Configuration options for the target application."""
from django.apps import AppConfig


class TargetConfig(AppConfig):
    """Configuration options for the target application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'target'
