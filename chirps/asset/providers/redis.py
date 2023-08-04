"""Logic for interfacing with a Redis asset."""
from logging import getLogger

import numpy as np
from asset.models import BaseAsset, PingResult, SearchResult
from django.db import models
from redis import Redis, exceptions
from redis.commands.search.query import Query

logger = getLogger(__name__)


class RedisAsset(BaseAsset):
    """Implementation of a Redis asset."""

    host = models.CharField(max_length=1048)
    port = models.PositiveIntegerField()
    database_name = models.CharField(max_length=256)
    username = models.CharField(max_length=256)
    password = models.CharField(max_length=2048, blank=True, null=True)

    index_name = models.CharField(max_length=256)
    text_field = models.CharField(max_length=256)
    embedding_field = models.CharField(max_length=256)
    embedding_model = models.CharField(max_length=256, default='text-embedding-ada-002')
    embedding_model_service = models.CharField(max_length=256, default='OpenAI')

    # Name of the file in the ./asset/static/ directory to use as a logo
    html_logo = 'asset/redis-logo.png'
    html_name = 'Redis'
    html_description = 'Redis Vector Database'

    REQUIRES_EMBEDDINGS = True
    HAS_PING = True

    def search(self, query: list, max_results: int) -> list[SearchResult]:
        """Search the Redis asset with the specified query."""
        client = Redis(
            host=self.host,
            port=self.port,
            db=self.database_name,
            password=self.password,
            username=self.username,
        )
        try:
            index = client.ft(self.index_name)

            score_field = 'vec_score'
            vector_param = 'vec_param'

            vss_query = f'*=>[KNN {max_results} @{self.embedding_field} ${vector_param} AS {score_field}]'
            return_fields = [self.embedding_field, self.text_field, score_field]

            search_query = (
                Query(vss_query).sort_by(score_field).paging(0, max_results).return_fields(*return_fields).dialect(2)
            )
            embedding = np.array(query, dtype=np.float32).tostring()
            params: dict[str, float] = {vector_param: embedding}
            results = index.search(search_query, query_params=params)

            docs = [SearchResult(data=doc[self.text_field], source_id=doc.id) for doc in results.docs]
            return docs
        finally:
            client.close()

    def test_connection(self) -> PingResult:
        """Ensure that the Redis asset can be connected to."""
        client = Redis(
            host=self.host,
            port=self.port,
            db=self.database_name,
            password=self.password,
            username=self.username,
        )
        try:
            # Basic ping
            result = client.ping()

            # Make sure the index exists
            try:
                info = client.ft(self.index_name).info()

                # Build a list of the available attributes
                # The second item in each element is the attribute name, as a byte value.
                # Also, decode it to a string while we're at it.
                attribute_names = [attr[1].decode() for attr in info['attributes']]

                # Ensure that the content and embeddings field names are present as attributes for the index
                if self.text_field not in attribute_names:
                    return PingResult(
                        success=False, error=f"Index '{self.index_name}' does not have a '{self.text_field}' field."
                    )

                if self.embedding_field not in attribute_names:
                    return PingResult(
                        success=False,
                        error=f"Index '{self.index_name}' does not have a '{self.embedding_field}' field.",
                    )

            except exceptions.ResponseError as err:
                if 'Unknown Index name' in str(err):
                    return PingResult(success=False, error=f"Index '{self.index_name}' does not exist.")

            client.close()
            return PingResult(success=result)
        except exceptions.ConnectionError as err:
            client.close()
            return PingResult(success=False, error=str(err))
