"""Embedding application configuration options."""
from django.apps import AppConfig


class EmbeddingConfig(AppConfig):
    """Configuration for the embedding app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'embedding'
