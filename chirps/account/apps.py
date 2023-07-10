"""Configures the account app.""" ''
from django.apps import AppConfig


class AccountConfig(AppConfig):
    """Configuration options for the account application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account'
