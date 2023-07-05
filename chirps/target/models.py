"""Models for the target appliation."""
import pinecone

from django.contrib import admin
from django.db import models
from fernet_fields import EncryptedCharField
from mantium_client.api_client import MantiumClient
from mantium_spec.api.applications_api import ApplicationsApi
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin
from polymorphic.models import PolymorphicModel

from django.contrib.auth.models import User
from django.templatetags.static import static

class BaseTarget(PolymorphicModel):
    """Base class that all targets will inherit from."""

    name = models.CharField(max_length=128)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def search(self, query: str, max_results: int) -> list[str]:
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

    # Name of the file in the ./target/static/ directory to use as a logo
    html_logo = 'target/redis-logo.png'
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

class PineconeTarget(BaseTarget):  
    """Implementation of a Pinecone target."""  
  
    api_key = models.CharField(max_length=256)  
    environment = models.CharField(max_length=256, blank=True, null=True)  
    index_name = models.CharField(max_length=256, blank=True, null=True)  
    project_name = models.CharField(max_length=256, blank=True, null=True)  
  
    # Name of the file in the ./target/static/ directory to use as a logo  
    html_logo = 'target/pinecone-logo.png'  
    html_name = 'Pinecone'  
    html_description = 'Pinecone Vector Database'  
  
import pinecone  
  
class PineconeTarget(BaseTarget):  
    # ... (existing code)  
  
    def search(self, query: str, max_results: int) -> list[str]:  
        """Search the Pinecone target with the specified query."""  
        pinecone.init(api_key=self.api_key, environment=self.environment)  
  
        # Assuming the query is converted to a vector of the same dimension as the index. We should re-visit this. 
        query_vector = convert_query_to_vector(query)  
  
        # Perform search on the Pinecone index  
        search_results = pinecone.fetch(index_name=self.index_name, query_vector=query_vector, top_k=max_results)  
  

        pinecone.deinit()  
        return search_results  
  
    def test_connection(self) -> bool:  
        """Ensure that the Pinecone target can be connected to."""  
        try:  
            pinecone.init(api_key=self.api_key, environment=self.environment)  
  
            index_description = pinecone.describe_index(self.index_name)  
            pinecone.deinit()  
            return True  
        except Exception as e:  
            print(f"Pinecone connection test failed: {e}")  
            return False  

class PineconeTargetAdmin(PolymorphicChildModelAdmin):  
    base_model = PineconeTarget  

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
        client = MantiumClient(client_id=self.client_id, client_secret=self.client_secret)
        apps_api = ApplicationsApi(client)

        query_request = {'query': query}
        results = apps_api.query_application(self.app_id, query_request)

        documents = [doc['content'] for doc in results['documents']]
        return documents


class MantiumTargetAdmin(PolymorphicChildModelAdmin):
    base_model = MantiumTarget

admin.site.register(RedisTarget)
admin.site.register(MantiumTarget)

targets = [RedisTarget, MantiumTarget, PineconeTarget]  

