---
layout: page
title: Add A Target
permalink: /add-a-target/
---


This guide will walk you through the process of adding a new target to the application by creating a custom `.py` file in the `/chirps/target/providers` subdirectory.

## Step 1: Create a New Target Model

Create a new `.py` file in the `/chirps/target/providers` subdirectory. Name the file after your target, for example: `my_target.py`.

## Step 2: Define the Target Model

In the newly created file, define a class for your target that inherits from the `BaseTarget` model. Here's an example using the `RedisTarget` model:

```python
from django.db import models
from target.models import BaseTarget

class RedisTarget(BaseTarget):
    """Implementation of a Redis target."""

    host = models.CharField(max_length=1048)
    port = models.PositiveIntegerField()
    database_name = models.CharField(max_length=256)
    username = models.CharField(max_length=256)
    password = models.CharField(max_length=2048, blank=True, null=True)

    index_name = models.CharField(max_length=256)
    text_field = models.CharField(max_length=256)
    embedding_field = models.CharField(max_length=256)

    html_logo = 'target/redis-logo.png'
    html_name = 'Redis'
    html_description = 'Redis Vector Database'

    REQUIRES_EMBEDDINGS = True
```

Customize the fields, properties, and methods as needed for your specific target.

## Step 3: Implement Search and Test Connection Methods

Define the `search()` and `test_connection()` methods for your target model. These methods allow the target to perform searches and test its connection to the database. Here's an example from the `PineconeTarget` model:

```python
def search(self, query: list, max_results: int) -> list[str]:
    """Search the Pinecone target with the specified query."""
    # Implementation details ...

def test_connection(self) -> bool:
    """Ensure that the Pinecone target can be connected to."""
    # Implementation details ...
```

## Step 4: Create a ModelForm for the Target Model

In the `target/forms.py` file, create a new `ModelForm` for your target model. This form will be used to render and validate the target model in the user interface. Here's an example using the `RedisTargetForm`:

```python
from .providers.my_target import MyTarget

class MyTargetForm(ModelForm):
    """Form for the MyTarget model."""

    class Meta:
        model = MyTarget
        fields = [
            # List the fields you want to include in the form
        ]

        widgets = {
            # Define the widgets for each field with the appropriate HTML attributes
        }
```

## Step 5: Register the Target Model and Form

In the `target/forms.py` file, add your new target model and form to the `targets` list:

```python
targets = [
    {'form': RedisTargetForm, 'model': RedisTarget},
    # ...
    {'form': MyTargetForm, 'model': MyTarget},
]
```

This will make your new target model and form available in the application.

## Step 6: Test Your New Target

After completing these steps, start the application and test your new target by navigating to the "Add Target" page. Ensure that the target is working correctly by performing searches and testing its connection to the database.

Congratulations! You have successfully added a new target to the application.
