"""Tests for the scan application."""
import time
from unittest.mock import patch

import pytest
from account.models import Profile
from asset.providers.pinecone import PineconeAsset
from celery import shared_task
from celery.contrib.testing.app import TestApp
from celery.contrib.testing.worker import start_worker
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from policy.models import Policy, PolicyVersion, Rule
from severity.models import Severity

from .models import ScanAsset, ScanAssetFailure
from .tasks import task_failure_handler


@pytest.mark.usefixtures('celery_session_worker')
class ScanTest(TestCase):
    """Test the scan application."""

    fixtures = ['scan/test_dash_pagination.json', 'severity/default_severities.json']

    def setUp(self):
        """Login the user before performing any tests"""
        self.client.post(reverse('login'), {'username': 'admin', 'password': 'admin'})

        # Create a profile for the user
        user = User.objects.get(username='admin')
        Profile.objects.create(user=user)

    def test_scan_dashboard_no_pagination(self):
        """Verify that no pagination widget is displayed when there are less than 25 items."""
        response = self.client.get(reverse('scan_dashboard'))

        # No pagination widget should be present
        # Ensure the element ID is not found
        self.assertNotContains(response, 'chirps-pagination-widget', status_code=200)

        # All 3 scans should be present (look for the element IDs)
        for scan_id in ['4', '5', '6']:
            self.assertContains(response, f'chirps-scan-{scan_id}', status_code=200)

    def test_scan_dashboard_pagination(self):
        """Verify that the 3 pages are available and that the pagination widget is displayed."""
        # First page
        response = self.client.get(reverse('scan_dashboard'), {'item_count': 1})
        self.assertContains(response, 'chirps-pagination-widget', status_code=200)
        self.assertContains(response, 'chirps-scan-4', status_code=200)

        # Second page
        response = self.client.get(reverse('scan_dashboard'), {'item_count': 1, 'page': 2})
        self.assertContains(response, 'chirps-pagination-widget', status_code=200)
        self.assertContains(response, 'chirps-scan-5', status_code=200)

        # Third page
        response = self.client.get(reverse('scan_dashboard'), {'item_count': 1, 'page': 3})
        self.assertContains(response, 'chirps-pagination-widget', status_code=200)
        self.assertContains(response, 'chirps-scan-6', status_code=200)

    def test_scan_dashboard_last_page(self):
        """If the page number exceeds the number of pages, verify that the last page is returned"""
        response = self.client.get(reverse('scan_dashboard'), {'item_count': 1, 'page': 100})
        self.assertContains(response, 'chirps-pagination-widget', status_code=200)
        self.assertContains(response, 'chirps-scan-6', status_code=200)

    def test_scan_requires_openai_key(self):
        """Test that a scan requires the user's OpenAI key"""
        # Create a new policy with a rule
        user = User.objects.get(username='admin')
        policy = Policy.objects.create(name='Test Policy', user=user)
        policy_version = PolicyVersion.objects.create(number=1, policy=policy)
        policy.current_version = policy_version
        policy.save()
        severity = Severity.objects.get(value=1)
        Rule.objects.create(query_string='some query', policy=policy_version, severity=severity)

        asset = PineconeAsset.objects.create(user=user, api_key='foo')
        asset.save()

        # Trigger a scan for the new policy
        with patch('scan.views.scan_task', dummy_task):
            response = self.client.post(
                reverse('scan_create'),
                {'policies': [policy.id], 'assets': [asset.id], 'description': 'test scan requiring OpenAI key'},
            )

        # The scan should fail as the user doesn't have an OpenAI key configured
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'User has not configured their OpenAI API key')

        # Check if ScanAsset object was not created
        self.assertFalse(ScanAsset.objects.filter(scan__description='test scan requiring OpenAI key').exists())


@shared_task(on_failure=task_failure_handler)
def dummy_task(*args, **kwargs):
    """Monkeypatched scan task that raises an exception."""
    raise Exception('Dummy exception')   # pylint: disable=broad-exception-raised


class ScanCeleryTests(TransactionTestCase):
    """Test the Celery job mechanism for scans."""

    fixtures = ['scan/test_dash_pagination.json', 'severity/default_severities.json']

    def setUp(self):
        """Login the user before performing any tests"""
        self.client.post(reverse('login'), {'username': 'admin', 'password': 'admin'})

        celery_config = {
            'accept_content': {'json'},
            'broker_heartbeat': 0,
            'broker_url': 'memory://',
            'enable_utc': True,
            'result_backend': 'django-db',  # We need to use the Django DB backend to query task results
            'timezone': 'UTC',
            'worker_hijack_root_logger': False,
            'worker_log_color': False,
        }

        app = TestApp(config=celery_config)
        self.celery_worker = start_worker(app)
        self.celery_worker.__enter__()

    def tearDown(self):
        """Ensure the Celery worker is stopped after each test."""
        self.celery_worker.__exit__(None, None, None)

    def test_scan_failure(self):
        """Given a failed scan, ensure that the UI renders the failure message."""
        with patch('scan.views.scan_task', dummy_task):
            response = self.client.post(
                reverse('scan_create'), {'policies': [100], 'assets': [1], 'description': 'test scan'}
            )

            # Should redirect the user back to the dashboard
            self.assertRedirects(response, '/scan/', status_code=302)

            # Wait for the scan asset to reach a failed state
            total_wait = 5

            while ScanAssetFailure.objects.all().count() == 0 and total_wait > 0:
                time.sleep(0.5)
                total_wait -= 0.5

            # Make sure the scan asset poll didn't timeout
            self.assertGreater(total_wait, 0)

        # Verify that the scan is available in the dashboard
        response = self.client.get(reverse('scan_dashboard'))

        # Given the current state of the fixtures, the latest scan should be ID #7
        self.assertContains(response, 'chirps-scan-7', status_code=200)

        # Obtain the ID of the ScanAsset instance created for the scan
        scan_asset = ScanAsset.objects.get(scan__id=7)

        # Open the scan details page
        response = self.client.get(reverse('scan_asset_status', kwargs={'scan_asset_id': scan_asset.id}))

        # Verify the scan asset status contains the proper error message
        self.assertContains(response, 'Dummy exception', status_code=286)
