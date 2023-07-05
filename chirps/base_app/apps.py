"""Application configration for the base_app app."""
from django.apps import AppConfig


class BaseAppConfig(AppConfig):
    """Application configration for the base_app app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base_app'
