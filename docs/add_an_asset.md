---
layout: page
title: Add An Asset
permalink: /add-an-asset/
---


This guide will walk you through the process of adding a new asset to the application by creating a custom `.py` file in the `/chirps/asset/providers` subdirectory.

## Step 1: Create a New Asset Model

Create a new `.py` file in the `/chirps/asset/providers` subdirectory. Name the file after your asset, for example: `my_asset.py`.

## Step 2: Define the Asset Model

In the newly created file, define a class for your asset that inherits from the `BaseAsset` model. Here's an example using the `RedisAsset` model:

```python
from django.db import models
from asset.models import BaseAsset

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

    html_logo = 'asset/redis-logo.png'
    html_name = 'Redis'
    html_description = 'Redis Vector Database'

    REQUIRES_EMBEDDINGS = True
```

Customize the fields, properties, and methods as needed for your specific asset.

## Step 3: Implement Search and Test Connection Methods

Define the `search()` and `test_connection()` methods for your asset model. These methods allow the asset to perform searches and test its connection to the database. Here's an example from the `PineconeAsset` model:

```python
def search(self, query: list, max_results: int) -> list[str]:
    """Search the Pinecone asset with the specified query."""
    # Implementation details ...

def test_connection(self) -> bool:
    """Ensure that the Pinecone asset can be connected to."""
    # Implementation details ...
```

## Step 4: Create a ModelForm for the Asset Model

In the `asset/forms.py` file, create a new `ModelForm` for your asset model. This form will be used to render and validate the asset model in the user interface. Here's an example using the `RedisAssetForm`:

```python
from .providers.my_asset import MyAsset

class MyAssetForm(ModelForm):
    """Form for the MyAsset model."""

    class Meta:
        model = MyAsset
        fields = [
            # List the fields you want to include in the form
        ]

        widgets = {
            # Define the widgets for each field with the appropriate HTML attributes
        }
```

## Step 5: Register the Asset Model and Form

In the `asset/forms.py` file, add your new asset model and form to the `assets` list:

```python
assets = [
    {'form': RedisAssetForm, 'model': RedisAsset},
    # ...
    {'form': MyAssetForm, 'model': MyAsset},
]
```

This will make your new asset model and form available in the application.

## Step 6: Test Your New Asset

After completing these steps, start the application and test your new asset by navigating to the "Add Asset" page. Ensure that the asset is working correctly by performing searches and testing its connection to the database.

Congratulations! You have successfully added a new asset to the application.
