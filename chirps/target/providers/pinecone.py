"""Logic for interfacing with a Pinecone target."""
from logging import getLogger

import pinecone as pinecone_lib
from django.db import models
from target.custom_fields import CustomEncryptedCharField
from target.models import BaseTarget

logger = getLogger(__name__)


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

    REQUIRES_EMBEDDINGS = True

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

    def search(self, query: list, max_results: int) -> list[str]:
        """Search the Pinecone target with the specified query."""
        pinecone_lib.init(api_key=self.api_key, environment=self.environment)

        # Perform search on the Pinecone index
        index = pinecone_lib.Index('chirps-test')
        search_results = index.query(vector=query, top_k=max_results, include_metadata=True)
        result_content = [r['metadata']['content'] for r in search_results['matches']]

        print(result_content)

        return result_content

    def test_connection(self) -> bool:
        """Ensure that the Pinecone target can be connected to."""
        try:
            pinecone_lib.init(api_key=self.api_key, environment=self.environment)
            pinecone_lib.deinit()
            return True
        except Exception as err:   # pylint: disable=broad-exception-caught
            logger.error('Pinecone connection test failed', extra={'error': err})
            return False
