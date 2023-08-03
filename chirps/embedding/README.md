# Add a New Embedding Model Service

This guide explains the steps required to add a new embedding model service and associated embedding model(s) to the application.

## Step 1: Add a new service enumeration

In the `embedding/models.py` file, add a new enumeration to the `Service` class inside the `Embedding` model. The enumeration should have a unique key and a human-readable name.

```python
MY_NEW_SERVICE = 'my_new_service', 'My New Service'
```

## Step 2: Create a new provider class

Create a new provider class for your service in the `embedding/providers` directory. The new provider class should inherit from `BaseEmbeddingProvider` and implement the required methods.

For example, create a file named `my_new_service.py` with the following content:
```python
class MyNewServiceEmbeddingProvider(BaseEmbeddingProvider):
    """MyNewService implementation for embedding provider."""

    def embed(self, user: User, model: str, text: str) -> Any:
        """Use MyNewService to generate embeddings for the specified text."""
        ...implement the function
```

## Step 3: Update the `get_provider_from_service_name` method

Return to the `embedding/models.py` file and update the `get_provider_from_service_name` method inside the `Service` class to include your new service and its provider class.

```python
@classmethod
def get_provider_from_service_name(cls, name: str) -> BaseEmbeddingProvider:
    embedding_service_providers = {
        Embedding.Service.OPEN_AI: OpenAIEmbeddingProvider,
        Embedding.Service.COHERE: CohereEmbeddingProvider,
        Embedding.Service.MY_NEW_SERVICE: MyNewServiceEmbeddingProvider, # Add this line
    }
    # ...
```

## Step 4: Add available models for your service

While still in the `embedding/models.py` file, update the `get_models_for_service` method inside the `Embedding` model to include the available model(s) for your new service.

```python
@staticmethod
def get_models_for_service(service):
    embedding_service_models = {
        # ...
        Embedding.Service.MY_NEW_SERVICE: [
            ('my_model_1', 'My Model 1'),
            ('my_model_2', 'My Model 2'),
        ],
    }
    # ...
```

## Step 5: Test your new service

Make sure to test your new service and associated embedding models by creating test cases in `embedding/tests.py`.
