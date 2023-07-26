"""Utility functions for the embedding app."""
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Embedding
from .providers.base import BaseEmbeddingProvider


def create_embedding(text: str, model: str, service: str, user: User | None) -> Embedding:
    """Pull an embedding from the database, or generate a new one."""
    # Search for the text to see if an embedding already exists
    try:
        query = Q(text=text, model=model, service=service)

        # If the user is specified, we need to search for embeddings
        # that are either owned by the user or nobody (templates)
        if user:
            query = query & (Q(user=user) | Q(user=None))

        embedding = Embedding.objects.get(query)

    except Embedding.DoesNotExist:
        # We need to generate a new embedding!
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
