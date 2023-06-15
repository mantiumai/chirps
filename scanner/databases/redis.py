from os import getenv

import numpy as np
from redis import Redis
from redis.commands.search.query import Query


class RedisDocumentStore:
    """Connect to a Redis database."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        database: int | None = None,
        username: str | None = None,
        password: str | None = None,
        index_name: str | None = None,
        distance_metric: str = 'cosine',
        embedding_field: str = 'embeddings',
    ) -> None:
        """Initialize the RedisDocumentStore."""
        self.host = host or getenv('REDIS_HOST', 'localhost')
        self.port = port or getenv('REDIS_PORT', 12000)
        self.database = database or getenv('REDIS_DATABASE', 0)
        self.username = username or getenv('REDIS_USERNAME')
        self.password = password or getenv('REDIS_PASSWORD')

        # Instantiate a client to the Redis server for this destination
        self.client = Redis(
            host=self.host,  # type: ignore
            port=self.port,  # type: ignore
            db=self.database,  # type: ignore
            password=self.password,
            username=self.username,
        )

        self.index_name = index_name
        self.index = self.client.ft(self.index_name)    # type: ignore
        self.distance_metric = distance_metric
        self.embedding_field = embedding_field

    def _scale_to_unit_interval(self, score: float) -> float:
        # cosine is the only supported distance metric
        if self.distance_metric == 'cosine':
            return (score + 1) / 2

        return score

    def query_by_embedding(self, query_emb: list[float], top_k: int) -> list[str]:
        """Query documents by embedding."""
        score_field = 'vec_score'
        vector_param = 'vec_param'

        vss_query = f'*=>[KNN {top_k} @{self.embedding_field} ${vector_param} AS {score_field}]'
        return_fields = [self.embedding_field, 'document_id', 'sync_file_id', score_field]

        query = Query(vss_query).sort_by(score_field).paging(0, top_k).return_fields(*return_fields).dialect(2)
        embedding = np.array(query_emb, dtype=np.float32).tostring()    # type: ignore
        params: dict[str, float] = {vector_param: embedding}
        results = self.index.search(query, query_params=params)

        embeddings = [doc.embeddings for doc in results.docs]
        return embeddings
