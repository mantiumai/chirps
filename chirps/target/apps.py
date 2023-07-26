"""Configuration options for the asset application."""
from django.apps import AppConfig


class TargetConfig(AppConfig):
    """Configuration options for the asset application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'asset'
