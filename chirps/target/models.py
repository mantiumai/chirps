"""Models for the target appliation."""
import requests
from django.contrib import admin
from django.db import models
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin
from polymorphic.models import PolymorphicModel


class BaseTarget(PolymorphicModel):
    """Base class that all targets will inherit from."""

    name = models.CharField(max_length=128)

    def search(self, query: str, max_results: int) -> list[str]:
        """Perform a query against the specified target, returning the max_results number of matches."""

    def test_connection(self) -> bool:
        """Verify that the target can be connected to."""

    def __str__(self):
        return self.name


class BaseTargetAdmin(PolymorphicParentModelAdmin):
    base_model = BaseTarget


class RedisTarget(BaseTarget):
    """Implementation of a Redis target."""

    host = models.CharField(max_length=1048)
    port = models.IntegerField()
    database_name = models.CharField(max_length=256)
    username = models.CharField(max_length=256)
    password = models.CharField(max_length=2048, blank=True, null=True)

    # Name of the file in the ./target/static/ directory to use as a logo
    html_logo = 'redis-logo.png'
    html_name = 'Redis'
    html_description = 'Redis Vector Database'

    def search(self, query: str, max_results: int) -> str:
        """Search the Redis target with the specified query."""
        print('Starting RedisTarget search')
        print('Converting search query into an embedding vector')
        print('RedisTarget search copmlete')

    def test_connection(self) -> bool:
        """Ensure that the Redis target can be connected to."""
        return True


class RedisTargetAdmin(PolymorphicChildModelAdmin):
    base_model = RedisTarget


admin.site.register(RedisTarget)


class MantiumTarget(BaseTarget):
    """Implementation of a Mantium target."""

    app_id = models.CharField(max_length=256)
    token = models.CharField(max_length=2048)
    top_k = models.IntegerField(default=100)

    # Name of the file in the ./target/static/ directory to use as a logo
    html_logo = 'mantiumai-logo.png'
    html_name = 'Mantium'
    html_description = 'Mantium Knowledge Vault'

    def search(self, query: str, max_results: int) -> list[str]:

        url = f'https://{self.app_id}.apps.mantiumai.com/chatgpt/query'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }

        result = requests.post(url=url, headers=headers, json={'queries': [query]})
        result.raise_for_status()
        return result.json()


targets = [RedisTarget, MantiumTarget]
