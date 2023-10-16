"""Test cases for the asset application."""
import json
from unittest import mock

import fakeredis
from asset.forms import APIEndpointAssetForm, PineconeAssetForm, RedisAssetForm
from asset.models import PingResult
from asset.providers.api_endpoint import APIEndpointAsset
from asset.providers.mantium import MantiumAsset
from asset.providers.redis import RedisAsset
from django.contrib.auth.models import User  # noqa: E5142
from django.test import TestCase
from django.urls import reverse
from embedding.models import Embedding
from parameterized import parameterized


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

    @parameterized.expand(
        [
            ('Flat headers and body', {'Content-Type': 'application/json'}, {'data': '%query%'}),
            (
                'Nested headers and flat body',
                {'Content-Type': 'application/json', 'custom': {'nested': 'yes'}},
                {'data': '%query%'},
            ),
            ('Flat headers and nested body', {'Content-Type': 'application/json'}, {'data': {'nested': 'yes'}}),
            (
                'Nested headers and nested body',
                {'Content-Type': 'application/json', 'custom': {'nested': 'yes'}},
                {'data': {'nested': 'yes'}},
            ),
        ]
    )
    def test_api_endpoint_asset_creation(self, _, headers, body):
        """Test the creation of an API Endpoint asset with the dropdown."""
        self.client.post(
            reverse('login'),
            {
                'username': self.users[0]['username'],
                'password': self.users[0]['password'],
            },
        )

        form_data = {
            'name': 'API Endpoint Asset',
            'description': 'Test API Endpoint Asset',
            'url': 'https://api.example.com/endpoint',
            'authentication_method': 'Bearer',
            'api_key': 'example-api-key',
            'headers': json.dumps(headers),
            'body': json.dumps(body),
            'timeout': '30',
        }
        form = APIEndpointAssetForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

        response = self.client.post(reverse('asset_create', args=['API Endpoint']), form_data)
        self.assertRedirects(response, reverse('asset_dashboard'))

        # Check if the data is properly stored in the database
        user = User.objects.get(username=self.users[0]['username'])
        api_endpoint_asset = APIEndpointAsset.objects.filter(user=user).first()
        self.assertIsNotNone(api_endpoint_asset)
        self.assertEqual(api_endpoint_asset.name, form_data['name'])
        self.assertEqual(api_endpoint_asset.url, form_data['url'])
        self.assertEqual(api_endpoint_asset.authentication_method, form_data['authentication_method'])
        self.assertEqual(api_endpoint_asset.api_key, form_data['api_key'])
        self.assertEqual(api_endpoint_asset.headers, json.loads(form_data['headers']))
        self.assertEqual(api_endpoint_asset.body, json.loads(form_data['body']))


class AssetPaginationTests(TestCase):
    """Test the scan application."""

    fixtures = ['asset/test_dash_pagination.json', 'severity/default_severities.json']

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
            result = asset.test_connection()
            assert result.success is False


class APIEndpointAssetTests(TestCase):
    """Test the APIEndpointAsset."""

    def setUp(self):
        """Set up the APIEndpointAsset tests."""
        # Login the user before performing any tests
        self.client.post(reverse('login'), {'username': 'admin', 'password': 'admin'})

        # Create an APIEndpointAsset instance for testing
        self.api_endpoint_asset = APIEndpointAsset.objects.create(
            name='Test API Endpoint Asset',
            url='https://api.example.com/endpoint',
            authentication_method='Bearer',
            api_key='example-api-key',
            headers='{"Content-Type": "application/json"}',
            body='{"data": "%query%"}',
        )

    def test_fetch_api_data(self):
        """Test that the search method sends the request and processes the response."""
        # Define the mocked response data
        mock_response_data = {
            'chat': {
                'instance': '46045911',
                'application': '1077587932992295905',
                'conversation': '4022404441860560655',
                'speak': 'true',
                'avatarFormat': 'webm',
                'secure': 'true',
                'message': 'hello',
            }
        }

        # Mock the requests.post method to return the mocked response data
        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_response_data

            # Call the search method and assert the results
            search_results = self.api_endpoint_asset.fetch_api_data('test query')
            self.assertEqual(len(search_results), 1)

            # Assert that requests.post was called with the expected arguments
            expected_url = self.api_endpoint_asset.url
            expected_headers = json.loads(self.api_endpoint_asset.headers)
            expected_headers['Authorization'] = f'Bearer {self.api_endpoint_asset.api_key}'
            expected_body = self.api_endpoint_asset.body.replace('%query%', 'test query')

            mock_post.assert_called_once_with(expected_url, headers=expected_headers, json=expected_body, timeout=30)

            # Assert the search result attributes
            result = search_results['chat']
            self.assertEqual(result['instance'], '46045911')
            self.assertEqual(result['application'], '1077587932992295905')
            self.assertEqual(result['conversation'], '4022404441860560655')
            self.assertEqual(result['speak'], 'true')
            self.assertEqual(result['avatarFormat'], 'webm')
            self.assertEqual(result['secure'], 'true')
            self.assertEqual(result['message'], 'hello')

    def test_test_connection(self):
        """Test the test_connection method."""
        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200

            ping_result = self.api_endpoint_asset.test_connection()
            self.assertIsInstance(ping_result, PingResult)
            self.assertTrue(ping_result.success)
            self.assertIsNone(ping_result.error)

            expected_url = self.api_endpoint_asset.url
            expected_headers = json.loads(self.api_endpoint_asset.headers)
            expected_headers['Authorization'] = f'Bearer {self.api_endpoint_asset.api_key}'
            expected_body = self.api_endpoint_asset.body.replace('%query%', 'Test message')

            mock_post.assert_called_once_with(expected_url, headers=expected_headers, json=expected_body, timeout=30)

    def test_test_connection_failure(self):
        """Test the test_connection method when the API request fails."""
        mock_response_data = {'error': 'API request failed'}

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 400
            mock_post.return_value.json.return_value = mock_response_data

            ping_result = self.api_endpoint_asset.test_connection()
            self.assertIsInstance(ping_result, PingResult)
            self.assertFalse(ping_result.success)
            self.assertIn(mock_response_data['error'], ping_result.error)

            expected_url = self.api_endpoint_asset.url
            expected_headers = json.loads(self.api_endpoint_asset.headers)
            expected_headers['Authorization'] = f'Bearer {self.api_endpoint_asset.api_key}'
            expected_body = self.api_endpoint_asset.body.replace('%query%', 'Test message')

            mock_post.assert_called_once_with(expected_url, headers=expected_headers, json=expected_body, timeout=30)
