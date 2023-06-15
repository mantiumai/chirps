from os import getenv

from redis.client import Redis


class RedisDocumentStore:
    """Connect to a Redis database."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        database: int | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        """Initialize the RedisDocumentStore."""
        self.host = host or getenv('REDIS_HOST', 'localhost')
        self.port = port or getenv('REDIS_PORT', 12000)
        self.database = database or getenv('REDIS_DATABASE', 0)
        self.username = username or getenv('REDIS_USERNAME')
        self.password = password or getenv('REDIS_PASSWORD')

        # Instantiate a client to the Redis server for this destination
        self.client = Redis(host=host, port=port, db=database, password=password, username=username)    # type: ignore
