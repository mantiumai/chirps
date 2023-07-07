"""Models for the target appliation."""
from logging import getLogger

import pinecone
from django.contrib.auth.models import User
from django.db import models
from django.templatetags.static import static
from fernet_fields import EncryptedCharField
from mantium_client.api_client import MantiumClient
from mantium_spec.api.applications_api import ApplicationsApi
from polymorphic.models import PolymorphicModel

from .custom_fields import CustomEncryptedCharField

logger = getLogger(__name__)


class BaseTarget(PolymorphicModel):
    """Base class that all targets will inherit from."""

    name = models.CharField(max_length=128)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    html_logo = None

    def search(self, query: str, max_results: int) -> list[str]:
        """Perform a query against the specified target, returning the max_results number of matches."""

    def test_connection(self) -> bool:
        """Verify that the target can be connected to."""

    def logo_url(self) -> str:
        """Fetch the logo URL for the target."""
        return static(self.html_logo)

    def __str__(self) -> str:
        """String representation of this model."""
        return str(self.name)


class RedisTarget(BaseTarget):
    """Implementation of a Redis target."""

    host = models.CharField(max_length=1048)
    port = models.IntegerField()
    database_name = models.CharField(max_length=256)
    username = models.CharField(max_length=256)
    password = models.CharField(max_length=2048, blank=True, null=True)

    # Name of the file in the ./target/static/ directory to use as a logo
    html_logo = 'target/redis-logo.png'
    html_name = 'Redis'
    html_description = 'Redis Vector Database'

    def search(self, query: str, max_results: int) -> str:
        """Search the Redis target with the specified query."""
        logger.error('RedisTarget search not implemented')
        raise NotImplementedError

    def test_connection(self) -> bool:
        """Ensure that the Redis target can be connected to."""
        logger.error('RedisTarget search not implemented')
        raise NotImplementedError


class PineconeTarget(BaseTarget):
    """Implementation of a Pinecone target."""

    api_key = CustomEncryptedCharField(max_length=256, editable=True)
    environment = models.CharField(max_length=256, blank=True, null=True)
    index_name = models.CharField(max_length=256, blank=True, null=True)
    project_name = models.CharField(max_length=256, blank=True, null=True)

    # Name of the file in the ./target/static/ directory to use as a logo
    html_logo = 'target/pinecone-logo.png'
    html_name = 'Pinecone'
    html_description = 'Pinecone Vector Database'

    @property
    def decrypted_api_key(self):
        """Return the decrypted API key."""
        if self.api_key is not None:
            try:
                decrypted_value = self.api_key
                return decrypted_value
            except UnicodeDecodeError:
                return 'Error: Decryption failed'
        return None

    def search(self, query: str, max_results: int) -> list[str]:
        """Search the Pinecone target with the specified query."""
        pinecone.init(api_key=self.api_key, environment=self.environment)

        # Assuming the query is converted to a vector of the same dimension as the index. We should re-visit this.
        query_vector = convert_query_to_vector(query)   # pylint: disable=undefined-variable

        # Perform search on the Pinecone index
        search_results = pinecone.fetch(index_name=self.index_name, query_vector=query_vector, top_k=max_results)
        pinecone.deinit()
        return search_results

    def test_connection(self) -> bool:
        """Ensure that the Pinecone target can be connected to."""
        try:
            pinecone.init(api_key=self.api_key, environment=self.environment)
            pinecone.deinit()
            return True
        except Exception as err:   # pylint: disable=broad-exception-caught
            logger.error('Pinecone connection test failed', extra={'error': err})
            return False


class MantiumTarget(BaseTarget):
    """Implementation of a Mantium target."""

    app_id = models.CharField(max_length=256)
    client_id = models.CharField(max_length=256)
    client_secret = EncryptedCharField(max_length=256)
    top_k = models.IntegerField(default=100)

    # Name of the file in the ./target/static/ directory to use as a logo
    html_logo = 'target/mantiumai-logo.jpg'
    html_name = 'Mantium'
    html_description = 'Mantium Knowledge Vault'

    def search(self, query: str, max_results: int) -> list[str]:
        logger.info('Starting Mantium Target search', extra={'id': self.id})
        client = MantiumClient(client_id=self.client_id, client_secret=self.client_secret)
        apps_api = ApplicationsApi(client)

        query_request = {'query': query}
        results = apps_api.query_application(self.app_id, query_request)

        documents = [doc['content'] for doc in results['documents']]
        logger.info('Mantium target search complete', extra={'id': self.id})
        return documents


targets = [RedisTarget, MantiumTarget, PineconeTarget]
