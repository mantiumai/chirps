"""Test cases for the asset application."""
from unittest import mock

import fakeredis
import pytest
from asset.forms import PineconeAssetForm, RedisAssetForm
from asset.providers.mantium import MantiumAsset
from asset.providers.redis import RedisAsset
from django.contrib.auth.models import User  # noqa: E5142
from django.test import TestCase
from django.urls import reverse
from embedding.models import Embedding
from redis import exceptions


class AssetTests(TestCase):
    """Test the asset application."""

    def setUp(self):
        """Initialize the database with some dummy users."""
        self.users = [
            {'username': 'user1', 'email': 'user1@mantiumai.com', 'password': 'user1password'},
            {'username': 'user2', 'email': 'user2@mantiumai.com', 'password': 'user2password'},
        ]
        # Setup two users for testing
        for user in self.users:
            response = self.client.post(
                reverse('signup'),
                {
                    'username': user['username'],
                    'email': user['email'],
                    'password1': user['password'],
                    'password2': user['password'],
                },
            )

            self.assertRedirects(response, '/', 302)

        self.get_embedding_models_url = reverse('get_embedding_models')

    def test_asset_tenant_isolation(self):
        """Verify that assets are isolated to a single tenant."""
        # Create an asset for user1
        MantiumAsset.objects.create(
            name='Mantium Asset',
            app_id='12345',
            client_id='1234',
            client_secret='secret_dummy_value',
            user=User.objects.get(username='user1'),
        )

        # Verify that the asset is accessible to user1 (need to login first)
        response = self.client.post(
            reverse('login'),
            {
                'username': self.users[0]['username'],
                'password': self.users[0]['password'],
            },
        )
        self.assertRedirects(response, '/', status_code=302)
        response = self.client.get(reverse('asset_dashboard'))
        self.assertContains(response, 'Mantium Asset', status_code=200)

        # Verify that the is not accessible to user2 (need to login first)
        response = self.client.post(
            reverse('login'),
            {
                'username': self.users[1]['username'],
                'password': self.users[1]['password'],
            },
        )
        self.assertRedirects(response, '/', status_code=302)
        response = self.client.get(reverse('asset_dashboard'))
        self.assertNotContains(response, 'Mantium Asset', status_code=200)

    def test_redis_asset_creation(self):
        """Test the creation of a Redis asset with the dropdown."""
        self.client.post(
            reverse('login'),
            {
                'username': self.users[0]['username'],
                'password': self.users[0]['password'],
            },
        )

        form_data = {
            'name': 'Redis Asset',
            'host': 'localhost',
            'port': 6379,
            'database_name': 'redis-db',
            'username': 'guest',
            'password': 'guestpassword',
            'index_name': 'redis-index',
            'text_field': 'text',
            'embedding_field': 'embedding',
            'embedding_model': 'text-embedding-ada-002',
            'embedding_model_service': Embedding.Service.OPEN_AI,
        }
        form = RedisAssetForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

        response = self.client.post(reverse('asset_create', args=['Redis']), form_data)
        self.assertRedirects(response, reverse('asset_dashboard'))

    def test_pinecone_asset_creation(self):
        """Test the creation of a Pinecone asset with the dropdown."""
        self.client.post(
            reverse('login'),
            {
                'username': self.users[0]['username'],
                'password': self.users[0]['password'],
            },
        )

        form_data = {
            'name': 'Pinecone Asset',
            'api_key': 'pinecone-api-key',
            'environment': 'us-west4-gcp-free',
            'index_name': 'pinecone-index',
            'project_name': 'pinecone-project',
            'metadata_text_field': 'text',
            'embedding_model': 'text-embedding-ada-002',
            'embedding_model_service': Embedding.Service.OPEN_AI,
        }
        form = PineconeAssetForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

        response = self.client.post(reverse('asset_create', args=['Pinecone']), form_data)
        self.assertRedirects(response, reverse('asset_dashboard'))

    def test_get_embedding_models_view(self):
        """Ensure expected models are returned"""
        self.client.post(
            reverse('login'),
            {
                'username': self.users[0]['username'],
                'password': self.users[0]['password'],
            },
        )
        service = Embedding.Service.OPEN_AI
        response = self.client.get(self.get_embedding_models_url, {'service': service})

        self.assertEqual(response.status_code, 200)

        models = Embedding.get_models_for_service(service)
        returned_models = response.json()

        self.assertEqual(len(models), len(returned_models))
        self.assertEqual(set([model[0] for model in models]), set([model[0] for model in returned_models]))


class AssetPaginationTests(TestCase):
    """Test the scan application."""

    fixtures = ['asset/test_dash_pagination.json']

    def setUp(self):
        """Login the user before performing any tests."""
        self.client.post(reverse('login'), {'username': 'admin', 'password': 'admin'})

    def test_dashboard_no_pagination(self):
        """Verify that no pagination widget is displayed when there are less than 25 items."""
        response = self.client.get(reverse('asset_dashboard'))

        # No pagination widget should be present
        # Ensure the element ID is not found
        self.assertNotContains(response, 'chirps-pagination-widget', status_code=200)

        # All 3 scans should be present (look for the element IDs)
        for asset_id in ['1', '2', '3']:
            self.assertContains(response, f'chirps-asset-{asset_id}', status_code=200)

    def test_dashboard_pagination(self):
        """Verify that the 3 pages are available and that the pagination widget is displayed."""
        # First page
        response = self.client.get(reverse('asset_dashboard'), {'item_count': 1})
        self.assertContains(response, 'chirps-pagination-widget', status_code=200)
        self.assertContains(response, 'chirps-asset-1', status_code=200)

        # Second page
        response = self.client.get(reverse('asset_dashboard'), {'item_count': 1, 'page': 2})
        self.assertContains(response, 'chirps-pagination-widget', status_code=200)
        self.assertContains(response, 'chirps-asset-2', status_code=200)

        # Third page
        response = self.client.get(reverse('asset_dashboard'), {'item_count': 1, 'page': 3})
        self.assertContains(response, 'chirps-pagination-widget', status_code=200)
        self.assertContains(response, 'chirps-asset-3', status_code=200)

    def test_scan_dashboard_last_page(self):
        """If the page number exceeds the number of pages, verify that the last page is returned"""
        response = self.client.get(reverse('asset_dashboard'), {'item_count': 1, 'page': 100})
        self.assertContains(response, 'chirps-pagination-widget', status_code=200)
        self.assertContains(response, 'chirps-asset-3', status_code=200)


class RedisAssetTests(TestCase):
    """Test the RedisAsset"""

    def setUp(self):
        """Set up the RedisAsset tests"""
        # Login the user before performing any tests
        self.client.post(reverse('login'), {'username': 'admin', 'password': 'admin'})
        self.server = fakeredis.FakeServer()
        self.redis = fakeredis.FakeStrictRedis(server=self.server)

    def test_ping__success(self):
        """Test that connectivity check works"""
        self.server.connected = True

        with mock.patch('asset.providers.redis.Redis', return_value=self.redis):
            asset = RedisAsset(host='localhost', port=12000)
            assert asset.test_connection()

    def test_ping__failure(self):
        """Test that ping raises ConnectionError if the server is not connected"""
        self.server.connected = False

        with mock.patch('asset.providers.redis.Redis', return_value=self.redis):
            asset = RedisAsset(host='localhost', port=12000)
            with pytest.raises(exceptions.ConnectionError):
                assert asset.test_connection()
