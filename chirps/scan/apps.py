"""Configuration options for the scan app."""
from django.apps import AppConfig


class ScanConfig(AppConfig):
    """Configuration options for the scan application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scan'
