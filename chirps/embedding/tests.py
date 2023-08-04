"""Tests for the embedding app."""
# pylint: disable=consider-using-with
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import openai
from account.models import Profile
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse

from .models import Embedding

# Build the path to the fixtures directory
fixture_path = Path(__file__).parent.resolve() / Path('./fixtures/embedding')


class MockOpenAIResponse:
    """Mock the response from OpenAI"""

    def __init__(self, data):
        self.data = data

    def __getitem__(self, key):
        """Override __getitem__"""
        return self.data[key]


class MockEmbeddingData:
    """Mock embedding data contained in OpenAI response"""

    def __init__(self, embedding):
        self.embedding = embedding


def mock_openai_embedding_create(*args, **kwargs):
    """Return the same response shape as from OpenAI"""
    return {
        'id': 'fake_id',
        'object': 'list',
        'data': [
            {
                'id': 'ans_1234567890',
                'object': 'answer',
                'embedding': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                'usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
            }
        ],
        'usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
    }


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

    def test_get_embedding_models_view(self):
        """Ensure expected models are returned"""
        service = Embedding.Service.OPEN_AI
        response = self.client.get(reverse('embedding_models'), {'service': service})

        self.assertEqual(response.status_code, 200)

        models = Embedding.get_models_for_service(service)

        # Ensure that each model is returned in the response
        for model in models:
            self.assertContains(response, model[0])


class GenerateEmbeddingsTests(TestCase):
    """Test the generate_embeddings management command"""

    def setUp(self):
        """Set up for the tests in this class"""
        # Create a test user with a known username, password, and API keys for both OpenAI and Cohere
        self.test_username = 'testuser'
        self.test_password = 'testpassword'
        self.test_openai_key = 'fake_openai_key'
        self.test_cohere_key = 'fake_cohere_key'

        self.user = User.objects.create_user(
            username=self.test_username, password=self.test_password, email='testuser@example.com'
        )
        self.user.save()

        # Create a profile for the test user
        self.profile = Profile.objects.create(user=self.user)

        self.profile.openai_key = self.test_openai_key
        self.profile.cohere_key = self.test_cohere_key
        self.profile.save()

        self.test_query = 'some example query'

    def test_generate_embeddings_invalid_service(self):
        """Test generate_embeddings command with an invalid service."""
        with patch('builtins.input', return_value=self.test_username):
            with patch('getpass.getpass', return_value=self.test_password):
                with patch('builtins.input', side_effect=['999', '1', '1']):
                    with self.assertRaises(CommandError) as cm:
                        call_command('generate_embeddings')

        self.assertEqual(
            str(cm.exception),
            'Invalid selection. Please enter a valid number.',
        )

    @patch('openai.Embedding.create', side_effect=mock_openai_embedding_create)
    def test_generate_embeddings_valid_service(self, _mock_openai_embedding_create):
        """Test generate_embeddings command with a valid service and model."""
        existing_embedding_count = Embedding.objects.count()
        # Create a temporary JSON fixture
        temp_fixture = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_fixture.write(
            json.dumps(
                [
                    {
                        'model': 'embedding.rule',
                        'pk': 1,
                        'fields': {
                            'query_string': self.test_query,
                        },
                    }
                ]
            )
        )
        temp_fixture.close()

        # Mock the input and getpass functions to return the test user's credentials
        with patch('builtins.input', side_effect=['2', '1', self.test_username]):
            with patch('getpass.getpass', return_value=self.test_password):
                # Run the generate_embeddings command
                call_command('generate_embeddings')

        # Check if the embedding was created
        new_embedding_count = Embedding.objects.count()
        self.assertTrue(new_embedding_count > existing_embedding_count)

        # Clean up the temp fixture
        os.remove(temp_fixture.name)
