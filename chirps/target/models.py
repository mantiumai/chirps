"""Models for the target appliation."""
import numpy as np

from django.contrib import admin
from django.db import models
from fernet_fields import EncryptedCharField
from mantium_client.api_client import MantiumClient
from mantium_spec.api.applications_api import ApplicationsApi
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin
from polymorphic.models import PolymorphicModel

from django.contrib.auth.models import User
from django.templatetags.static import static

from redis import Redis
from redis.commands.search.query import Query

class BaseTarget(PolymorphicModel):
    """Base class that all targets will inherit from."""

    name = models.CharField(max_length=128)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    top_k = models.IntegerField(default=100)

    def search(self, rule, max_results: int) -> list[str]:
        """Perform a query against the specified target, returning the max_results number of matches."""

    def test_connection(self) -> bool:
        """Verify that the target can be connected to."""

    def logo_url(self) -> str:
        return static(self.html_logo)

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
    index_name = models.CharField(max_length=256)
    embedding_field = models.CharField(max_length=256)

    # Name of the file in the ./target/static/ directory to use as a logo
    html_logo = 'target/redis-logo.png'
    html_name = 'Redis'
    html_description = 'Redis Vector Database'
    
    # client = Redis(
    #     host=host,
    #     port=port,
    #     db=database_name,
    #     password=password,
    #     username=username,
    # )

    # def __init__(self, *args, **kwargs):
    #     self.client = Redis(
    #         host=self.host,
    #         port=self.port,
    #         db=self.database_name,
    #         password=self.password,
    #         username=self.username,
    #     )

    def search(self, rule, max_results: int) -> str:
        """Search the Redis target with the specified query."""
        score_field = 'vec_score'
        vector_param = 'vec_param'

        vss_query = f'*=>[KNN {self.top_k} @{self.embedding_field} ${vector_param} AS {score_field}]'
        return_fields = [self.embedding_field, 'document_id', 'sync_file_id', score_field]

        query = Query(vss_query).sort_by(score_field).paging(0, self.top_k).return_fields(*return_fields).dialect(2)
        embedding = np.array(rule.query_embedding, dtype=np.float32).tostring()    # type: ignore
        params: dict[str, float] = {vector_param: embedding}
        results = self.index.search(query, query_params=params)

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
        client.ping()

        return True


class RedisTargetAdmin(PolymorphicChildModelAdmin):
    base_model = RedisTarget


class MantiumTarget(BaseTarget):
    """Implementation of a Mantium target."""

    app_id = models.CharField(max_length=256)
    client_id = models.CharField(max_length=256)
    client_secret = EncryptedCharField(max_length=256)

    # Name of the file in the ./target/static/ directory to use as a logo
    html_logo = 'target/mantiumai-logo.jpg'
    html_name = 'Mantium'
    html_description = 'Mantium Knowledge Vault'

    def search(self, rule, max_results: int) -> list[str]:
        client = MantiumClient(client_id=self.client_id, client_secret=self.client_secret)
        apps_api = ApplicationsApi(client)

        query_request = {'query': rule.query_string}
        results = apps_api.query_application(self.app_id, query_request)

        documents = [doc['content'] for doc in results['documents']]
        return documents


class MantiumTargetAdmin(PolymorphicChildModelAdmin):
    base_model = MantiumTarget

admin.site.register(RedisTarget)
admin.site.register(MantiumTarget)

targets = [RedisTarget, MantiumTarget]
