"""Logic for interfacing with a Redis target."""
from logging import getLogger

from django.db import models
from redis import Redis

from target.models import BaseTarget

logger = getLogger(__name__)


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
        client = Redis(
            host=self.host,
            port=self.port,
            db=self.database_name,
            password=self.password,
            username=self.username,
        )
        return client.ping()
