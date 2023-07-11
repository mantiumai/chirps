"""Test cases for the target application."""
from unittest import mock

import fakeredis
import pytest
from django.contrib.auth.models import User  # noqa: E5142
from django.test import TestCase
from django.urls import reverse
from redis import exceptions
from target.providers.mantium import MantiumTarget
from target.providers.redis import RedisTarget


class TargetTests(TestCase):
    """Test the target application."""

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

    def test_target_tenant_isolation(self):
        """Verify that targets are isolated to a single tenant."""
        # Create a target for user1
        MantiumTarget.objects.create(
            name='Mantium Target',
            app_id='12345',
            client_id='1234',
            client_secret='secret_dummy_value',
            user=User.objects.get(username='user1'),
        )

        # Verify that the target is accessible to user1 (need to login first)
        response = self.client.post(
            reverse('login'),
            {
                'username': self.users[0]['username'],
                'password': self.users[0]['password'],
            },
        )
        self.assertRedirects(response, '/', status_code=302)
        response = self.client.get(reverse('target_dashboard'))
        self.assertContains(response, 'Mantium Target', status_code=200)

        # Verify that the is not accessible to user2 (need to login first)
        response = self.client.post(
            reverse('login'),
            {
                'username': self.users[1]['username'],
                'password': self.users[1]['password'],
            },
        )
        self.assertRedirects(response, '/', status_code=302)
        response = self.client.get(reverse('target_dashboard'))
        self.assertNotContains(response, 'Mantium Target', status_code=200)


class TargetPaginationTests(TestCase):
    """Test the scan application."""

    fixtures = ['target/test_dash_pagination.json']

    def setUp(self):
        """Login the user before performing any tests."""
        self.client.post(reverse('login'), {'username': 'admin', 'password': 'admin'})

    def test_dashboard_no_pagination(self):
        """Verify that no pagination widget is displayed when there are less than 25 items."""
        response = self.client.get(reverse('target_dashboard'))

        # No pagination widget should be present
        # Ensure the element ID is not found
        self.assertNotContains(response, 'chirps-pagination-widget', status_code=200)

        # All 3 scans should be present (look for the element IDs)
        for scan_id in ['1', '2', '3']:
            self.assertContains(response, f'chirps-target-{scan_id}', status_code=200)

    def test_dashboard_pagination(self):
        """Verify that the 3 pages are available and that the pagination widget is displayed."""
        # First page
        response = self.client.get(reverse('target_dashboard'), {'item_count': 1})
        self.assertContains(response, 'chirps-pagination-widget', status_code=200)
        self.assertContains(response, 'chirps-target-1', status_code=200)

        # Second page
        response = self.client.get(reverse('target_dashboard'), {'item_count': 1, 'page': 2})
        self.assertContains(response, 'chirps-pagination-widget', status_code=200)
        self.assertContains(response, 'chirps-target-2', status_code=200)

        # Third page
        response = self.client.get(reverse('target_dashboard'), {'item_count': 1, 'page': 3})
        self.assertContains(response, 'chirps-pagination-widget', status_code=200)
        self.assertContains(response, 'chirps-target-3', status_code=200)

    def test_scan_dashboard_last_page(self):
        """If the page number exceeds the number of pages, verify that the last page is returned"""
        response = self.client.get(reverse('target_dashboard'), {'item_count': 1, 'page': 100})
        self.assertContains(response, 'chirps-pagination-widget', status_code=200)
        self.assertContains(response, 'chirps-target-3', status_code=200)


class RedisTargetTests(TestCase):
    """Test the RedisTarget"""

    def setUp(self):
        """Set up the RedisTarget tests"""
        # Login the user before performing any tests
        self.client.post(reverse('login'), {'username': 'admin', 'password': 'admin'})
        self.server = fakeredis.FakeServer()
        self.redis = fakeredis.FakeStrictRedis(server=self.server)

    def test_ping__success(self):
        """Test that connectivity check works"""
        self.server.connected = True

        with mock.patch('target.providers.redis.Redis', return_value=self.redis):
            target = RedisTarget(host='localhost', port=12000)
            assert target.test_connection()

    def test_ping__failure(self):
        """Test that ping raises ConnectionError if the server is not connected"""
        self.server.connected = False

        with mock.patch('target.providers.redis.Redis', return_value=self.redis):
            target = RedisTarget(host='localhost', port=12000)
            with pytest.raises(exceptions.ConnectionError):
                assert target.test_connection()
