"""Logic for interfacing with a Redis target."""
from logging import getLogger

import numpy as np
from django.db import models
from redis import Redis
from redis.commands.search.query import Query
from target.models import BaseTarget

logger = getLogger(__name__)


class RedisTarget(BaseTarget):
    """Implementation of a Redis target."""

    host = models.CharField(max_length=1048)
    port = models.IntegerField()
    database_name = models.CharField(max_length=256)
    username = models.CharField(max_length=256)
    password = models.CharField(max_length=2048, blank=True, null=True)

    index_name = models.CharField(max_length=256)
    text_field = models.CharField(max_length=256)
    embedding_field = models.CharField(max_length=256)

    # Name of the file in the ./target/static/ directory to use as a logo
    html_logo = 'target/redis-logo.png'
    html_name = 'Redis'
    html_description = 'Redis Vector Database'

    def search(self, vectors: list, max_results: int) -> str:
        """Search the Redis target with the specified query."""
        client = Redis(
            host=self.host,
            port=self.port,
            db=self.database_name,
            password=self.password,
            username=self.username,
        )
        index = client.ft(self.index_name)

        score_field = 'vec_score'
        vector_param = 'vec_param'

        vss_query = f'*=>[KNN {max_results} @{self.embedding_field} ${vector_param} AS {score_field}]'
        return_fields = [self.embedding_field, self.text_field, score_field]

        query = Query(vss_query).sort_by(score_field).paging(0, max_results).return_fields(*return_fields).dialect(2)
        embedding = np.array(vectors, dtype=np.float32).tostring()    # type: ignore
        params: dict[str, float] = {vector_param: embedding}
        print(f'query: {query}')
        results = index.search(query, query_params=params)

        print(f'results: {results.docs}')

        return results.docs

    def test_connection(self) -> bool:
        """Ensure that the Redis target can be connected to."""
        client = Redis(
            host=self.host,
            port=self.port,
            db=self.database_name,
            password=self.password,
            username=self.username,
        )
        return client.ping()
