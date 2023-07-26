"""Utility functions for the embedding app."""
from logging import getLogger

from django.contrib.auth.models import User

from .models import Embedding
from .providers.base import BaseEmbeddingProvider

logger = getLogger(__name__)


def create_embedding(text: str, model: str, service: str, user: User) -> Embedding:
    """Pull an embedding from the database, or generate a new one."""
    # Search for the text to see if an embedding already exists
    try:
        logger.info(f'query text: {text}')
        embedding = Embedding.objects.get(
            text=text,
            model=model,
            service=service,
            user=user,
        )
        if embedding:
            logger.info('embedding found!')
    except Embedding.DoesNotExist:  # Oh noes! We need to generate a new embedding.
        # Fetch the required provider class from the name of the service requested by the user. The service name
        # should be one of the enum values found in Embedding.Service.
        provider: BaseEmbeddingProvider = Embedding.Service.get_provider_from_service_name(service)

        # Use the specified service to generate embeddings with the specified model
        # Raises EmbeddingError if the embedding fails
        embed_result = provider.embed(user=user, model=model, text=text)

        # Save the embedding result to the database
        embedding = Embedding.objects.create(
            model=model,
            service=service,
            text=text,
            vectors=embed_result,
            user=user,
        )

    return embedding
