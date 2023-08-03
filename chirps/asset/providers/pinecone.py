"""Logic for interfacing with a Pinecone asset."""
from logging import getLogger

import pinecone as pinecone_lib
from asset.models import BaseAsset, PingResult, SearchResult
from django.db import models
from fernet_fields import EncryptedCharField

logger = getLogger(__name__)


class PineconeAsset(BaseAsset):
    """Implementation of a Pinecone asset."""

    api_key = EncryptedCharField(max_length=256, editable=True)
    environment = models.CharField(max_length=256, blank=True, null=True)
    index_name = models.CharField(max_length=256, blank=True, null=True)
    project_name = models.CharField(max_length=256, blank=True, null=True)
    metadata_text_field = models.CharField(max_length=256, blank=False, null=True)
    embedding_model = models.CharField(max_length=256, default='text-embedding-ada-002')
    embedding_model_service = models.CharField(max_length=256, default='OpenAI')

    # Name of the file in the ./asset/static/ directory to use as a logo
    html_logo = 'asset/pinecone-logo.png'
    html_name = 'Pinecone'
    html_description = 'Pinecone Vector Database'

    REQUIRES_EMBEDDINGS = True
    HAS_PING = True

    @property
    def decrypted_api_key(self):
        """Return the decrypted API key~."""
        if self.api_key is not None:
            try:
                decrypted_value = self.api_key
                masked_value = decrypted_value[:4] + '*' * (len(decrypted_value) - 4)
                return masked_value
            except UnicodeDecodeError:
                return 'Error: Decryption failed'
        return None

    def search(self, query: list, max_results: int) -> list[SearchResult]:
        """Search the Pinecone asset with the specified query."""
        pinecone_lib.init(api_key=self.api_key, environment=self.environment)

        # Perform search on the Pinecone index
        index = pinecone_lib.Index(self.index_name)
        search_results = index.query(vector=query, top_k=max_results, include_metadata=True)

        metadata_text_field = self.metadata_text_field if self.metadata_text_field else 'content'
        result_content = [
            SearchResult(data=r['metadata'][metadata_text_field], source_id=r['id']) for r in search_results['matches']
        ]

        return result_content

    def test_connection(self) -> PingResult:
        """Ensure that the Pinecone asset can be connected to."""
        try:
            pinecone_lib.init(api_key=self.api_key, environment=self.environment)
            pinecone_lib.list_indexes()
            return PingResult(success=True)
        except Exception as err:   # pylint: disable=broad-exception-caught
            logger.error('Pinecone connection test failed', extra={'error': err})
            return PingResult(success=False, error=str(err))
