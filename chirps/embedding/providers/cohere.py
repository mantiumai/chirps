"""Cohere implementation for embedding provider."""
import logging
from typing import Any

import cohere
from django.contrib.auth.models import User

from .base import BaseEmbeddingProvider, EmbeddingError

logger = logging.getLogger(__name__)


class CohereEmbeddingProvider(BaseEmbeddingProvider):
    """Cohere implementation for embedding providers."""

    def embed(self, user: User, model: str, text: str) -> Any:
        """Use Cohere to generate embeddings for the specified text."""
        # If the Cohere API key is not set, raise an error
        if user.profile.cohere_key in [None, '']:
            logger.error('User Cohere key not set', extra={'user_id': user.id})
            raise EmbeddingError('Cohere API key not set')

        # Initialize the Cohere API key from the user's profile
        cohere_client = cohere.Client(user.profile.cohere_key)

        logger.debug('Generating embedding for text', extra={'text': text})

        # Generate the embedding
        try:
            response = cohere_client.embed(texts=[text], model=model)
        except Exception as err:
            raise EmbeddingError(f'Embedding failure: {str(err)}') from err

        logger.debug('Embedding complete', extra={'text': text})

        # Since we're only embedding one text, return the first embedding in the response
        return response['embeddings'][0]
