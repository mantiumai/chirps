"""Logic for interfacing with an API Endpoint Asset."""
from logging import getLogger

from asset.models import BaseAsset, PingResult, SearchResult
from django.db import models
from fernet_fields import EncryptedCharField

logger = getLogger(__name__)


class APIEndpointAsset(BaseAsset):
    """Implementation of an API Endpoint asset."""

    url = models.URLField(max_length=2048, blank=False, null=False)
    authentication_method = models.CharField(
        max_length=10, choices=[('Basic', 'Basic'), ('Bearer', 'Bearer')], default='Bearer'
    )
    api_key = EncryptedCharField(max_length=256, editable=True)
    headers = models.JSONField(blank=True, null=True)
    body = models.JSONField(blank=True, null=True)

    # Name of the file in the ./asset/static/ directory to use as a logo
    html_logo = 'asset/api-endpoint-logo.png'
    html_name = 'API Endpoint'
    html_description = 'Generic API Endpoint Asset'

    REQUIRES_EMBEDDINGS = False
    HAS_PING = True

    @property
    def decrypted_api_key(self):
        """Return the decrypted API key."""
        if self.api_key is not None:
            try:
                decrypted_value = self.api_key
                masked_value = decrypted_value[:4] + '*' * (len(decrypted_value) - 4)
                return masked_value
            except UnicodeDecodeError:
                return 'Error: Decryption failed'
        return None

    def search(self, query: str, max_results: int) -> list[SearchResult]:
        """Search the API Endpoint asset with the specified query."""
        raise NotImplementedError('The search method is not implemented for this asset.')

    def test_connection(self) -> PingResult:
        """Ensure that the API Endpoint asset can be connected to."""
        raise NotImplementedError('The test_connection method is not implemented for this asset.')

    def displayable_attributes(self):
        """Display a subset of the model's attributes"""
        return [
            {'label': 'URL', 'value': self.url},
            {'label': 'Authentication Method', 'value': self.authentication_method},
        ]
