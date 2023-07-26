"""Tests for the embedding app."""
# pylint: disable=consider-using-with
import json
from pathlib import Path
from unittest.mock import patch

import openai
from django.test import TestCase
from django.urls import reverse

from .models import Embedding

# Build the path to the fixtures directory
fixture_path = Path(__file__).parent.resolve() / Path('./fixtures/embedding')


class TestEmbedding(TestCase):
    """Test the embedding app."""

    def setUp(self):
        """Create a dummy user for testing."""
        username = 'test_user'
        password = 'test_password'
        email = 'test_user@mantiumai.com'

        # Create a new account (will automatically log us in)
        self.client.post(
            reverse('signup'), {'username': username, 'email': email, 'password1': password, 'password2': password}
        )

        # Set a dummy OpenAI key
        self.client.post(reverse('profile'), {'openai_key': 'test_openai_key'})

    def test_create_invalid(self):
        """Test creating an embedding with invalid URL parameters."""
        # Missing text field should yield a 400 response
        response = self.client.get(reverse('embedding_create'), {'model': 'test model', 'service': 'test service'})
        self.assertContains(response, text='"text": ["This field is required."]', status_code=400)

        # Missing model field should yield a 400 response
        response = self.client.get(reverse('embedding_create'), {'text': 'test text', 'service': 'test service'})
        self.assertContains(response, text='"model": ["This field is required."]', status_code=400)

        # Missing service field should yield a 400 response
        response = self.client.get(reverse('embedding_create'), {'text': 'test text', 'model': 'test model'})
        self.assertContains(response, text='"service": ["This field is required."]', status_code=400)

        # Pass in an invalid service ID
        response = self.client.get(
            reverse('embedding_create'), {'text': 'test text', 'model': 'test model', 'service': 'invalid service'}
        )
        self.assertContains(
            response,
            text='"service": ["Select a valid choice. invalid service is not one of the available choices."]',
            status_code=400,
        )

    @patch(
        'openai.Embedding.create',
        side_effect=openai.error.InvalidRequestError('The model `invalid-model-001` does not exist', ''),
    )
    def test_create_invalid_openai_model(self, _mock_openai_embedding_create):
        """Pass in a junk model name to the OpenAI service."""
        response = self.client.get(
            reverse('embedding_create'), {'text': 'test text', 'model': 'invalid-model-001', 'service': 'OpenAI'}
        )
        self.assertContains(
            response,
            text='{"error": "Embedding failure: The model `invalid-model-001` does not exist"}',
            status_code=400,
        )

    @patch(
        'openai.Embedding.create',
        return_value=json.loads(open(f'{fixture_path}/openai_embedding_create_mock.json', encoding='utf-8').read()),
    )
    def test_create_valid(self, _mock_openai_embedding_create):
        """Test creating a valid embedding."""
        # Verify there are no embeddings in the database
        self.assertEqual(0, Embedding.objects.all().count())

        # Fire off an embedding request that will hit the OpenAI mock
        # The request SHOULD create a new Embedding object in the database
        response = self.client.get(
            reverse('embedding_create'), {'text': 'test text', 'model': 'invalid-model-001', 'service': 'OpenAI'}
        )
        self.assertContains(response, text='-0.016634132713079453', count=2, status_code=200)

        # There now should be one embedding in the database
        self.assertEqual(1, Embedding.objects.all().count())

        # Fire off a duplicate request - verify there is still only one model in the DB
        response = self.client.get(
            reverse('embedding_create'), {'text': 'test text', 'model': 'invalid-model-001', 'service': 'OpenAI'}
        )
        self.assertContains(response, text='-0.016634132713079453', count=2, status_code=200)
        self.assertEqual(1, Embedding.objects.all().count())

    @patch(
        'openai.Embedding.create',
        return_value=json.loads(open(f'{fixture_path}/openai_embedding_create_mock.json', encoding='utf-8').read()),
    )
    def test_delete(self, _mock_openai_embedding_create):
        """Test deleting an embedding."""
        # Verify there are no embeddings in the database
        self.assertEqual(0, Embedding.objects.all().count())

        # Fire off an embedding request that will hit the OpenAI mock
        # The request SHOULD create a new Embedding object in the database
        response = self.client.get(
            reverse('embedding_create'), {'text': 'test text', 'model': 'invalid-model-001', 'service': 'OpenAI'}
        )
        self.assertContains(response, text='-0.016634132713079453', count=2, status_code=200)

        # List all of the embeddings (there should be only one)
        response = self.client.get(reverse('embedding_list'))
        json_data = response.json()
        self.assertEqual(len(json_data['embeddings']), 1)

        # Delete the embedding
        response = self.client.get(
            reverse('embedding_delete', kwargs={'embedding_id': json_data['embeddings'][0]['id']})
        )
        self.assertEqual(response.status_code, 200)

        # Verify the embedding is deleted from the database
        self.assertEqual(0, Embedding.objects.all().count())
