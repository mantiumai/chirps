"""Base implementation for embedding providers."""
from abc import ABC
from typing import Any

from django.contrib.auth.models import User


class EmbeddingError(Exception):
    """Error class for the embedding providers."""


class BaseEmbeddingProvider(ABC):
    """Base implementation for embedding providers."""

    def embed(self, user: User, model: str, text: str) -> Any:
        """Generate embeddings for the specified text."""
        raise NotImplementedError
