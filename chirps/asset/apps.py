"""Configuration options for the asset application."""
from django.apps import AppConfig


class AssetConfig(AppConfig):
    """Configuration options for the asset application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'asset'
