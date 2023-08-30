"""Logic for interfacing with an API Endpoint Asset."""
import json
from logging import getLogger

import requests
from asset.models import BaseAsset, PingResult
from django.db import models
from fernet_fields import EncryptedCharField
from requests import RequestException, Timeout

logger = getLogger(__name__)


class APIEndpointAsset(BaseAsset):
    """Implementation of an API Endpoint asset."""

    # what is the model served by this asset supposed to be doing?
    description = models.TextField(blank=True, null=True, max_length=2048)

    url = models.URLField(max_length=2048, blank=False, null=False)
    authentication_method = models.CharField(
        max_length=10, choices=[('Basic', 'Basic'), ('Bearer', 'Bearer')], default='Bearer'
    )
    api_key = EncryptedCharField(max_length=256, editable=True)
    headers = models.JSONField(blank=True, null=True)
    body = models.JSONField(blank=True, null=True, default={'data': '%query%'})
    timeout = models.IntegerField(default=30)

    # Name of the file in the ./asset/static/ directory to use as a logo
    html_logo = 'asset/api-endpoint-logo.svg'
    html_name = 'API Endpoint'
    html_description = 'Generic API Endpoint Asset'

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

    def fetch_api_data(self, query: str) -> dict:
        """Fetch data from the API using the provided query."""
        # Convert headers JSON string into a dictionary
        headers_dict = json.loads(self.headers) if self.headers else {}

        # Build the request headers
        headers = headers_dict.copy()
        if self.authentication_method == 'Bearer':
            headers['Authorization'] = f'Bearer {self.api_key}'
        elif self.authentication_method == 'Basic':
            headers['Authorization'] = f'Basic {self.api_key}'

        # Replace the %query% placeholder in the body
        body = json.loads(json.dumps(self.body).replace('%query%', query))

        # Send the request
        try:
            response = requests.post(self.url, headers=headers, json=body, timeout=self.timeout)
        except Timeout as exc:
            raise RequestException('Error: API request timed out') from exc

        # Check if the request was successful
        if response.status_code != 200:
            raise RequestException(f'Error: API request failed with status code {response.status_code}')

        # Parse the response and return the search results
        response_data = response.json()
        return response_data

    def test_connection(self) -> PingResult:
        """Ensure that the API Endpoint asset can be connected to."""
        raise NotImplementedError('The test_connection method is not implemented for this asset.')

    def displayable_attributes(self):
        """Display a subset of the model's attributes"""
        return [
            {'label': 'URL', 'value': self.url},
            {'label': 'Authentication Method', 'value': self.authentication_method},
        ]
