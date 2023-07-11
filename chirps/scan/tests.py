"""Tests for the scan application."""

from django.contrib.auth.models import User  # noqa: E5142
from django.test import TestCase
from django.urls import reverse
from target.providers.mantium import MantiumTarget


class ScanTest(TestCase):
    """Test the scan application."""

    fixtures = ['scan/test_dash_pagination.json']

    def setUp(self):
        # Login the user before performing any tests
        self.client.post(reverse('login'), {'username': 'admin', 'password': 'admin'})

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
