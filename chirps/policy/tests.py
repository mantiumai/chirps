"""Tests for the policy application."""

from unittest import skip

from django.test import TestCase
from django.urls import reverse

from .forms import PolicyForm


@skip('Disabling until pagination is re-added to the policy application.')
class PolicyPaginationTests(TestCase):
    """Test the policy application pagination."""

    fixtures = ['policy/employee.json', 'policy/network.json', 'policy/sensitive_data.json']

    def setUp(self):
        """Login the user before performing any tests."""
        self.client.post(
            reverse('signup'),
            {'username': 'admin', 'email': 'admin@mantiumai.com', 'password1': 'admin', 'password2': 'admin'},
        )

    def test_dashboard_no_pagination(self):
        """Verify that no pagination widget is displayed when there are less than 25 items."""
        response = self.client.get(reverse('policy_dashboard'))

        # No pagination widget should be present
        # Ensure the element ID is not found
        self.assertNotContains(response, 'chirps-pagination-widget', status_code=200)

        # All 3 scans should be present (look for the element IDs)
        for scan_id in ['100', '200', '300']:
            self.assertContains(response, f'chirps-policy-{scan_id}', status_code=200)

    def test_dashboard_pagination(self):
        """Verify that the 3 pages are available and that the pagination widget is displayed."""
        # First page
        response = self.client.get(reverse('policy_dashboard'), {'item_count': 1})
        self.assertContains(response, 'chirps-pagination-widget', status_code=200)
        self.assertContains(response, 'chirps-policy-100', status_code=200)

        # Second page
        response = self.client.get(reverse('policy_dashboard'), {'item_count': 1, 'page': 2})
        self.assertContains(response, 'chirps-pagination-widget', status_code=200)
        self.assertContains(response, 'chirps-policy-200', status_code=200)

        # Third page
        response = self.client.get(reverse('policy_dashboard'), {'item_count': 1, 'page': 3})
        self.assertContains(response, 'chirps-pagination-widget', status_code=200)
        self.assertContains(response, 'chirps-policy-300', status_code=200)

    def test_dashboard_last_page(self):
        """If the page number exceeds the number of pages, verify that the last page is returned"""
        response = self.client.get(reverse('policy_dashboard'), {'item_count': 1, 'page': 100})
        self.assertContains(response, 'chirps-pagination-widget', status_code=200)
        self.assertContains(response, 'chirps-policy-300', status_code=200)


class PolicyCreateForm(TestCase):
    """Test the custom logic in the policy create form."""

    def test_single_rule(self):
        """Verify that a single rule is parsed correctly."""
        rule_data = {
            'rule_name': 'Test Rule',
            'rule_query_string': 'Test Query String',
            'rule_regex': 'Test Regex',
            'rule_severity': 'Test Severity',
        }

        form = PolicyForm(
            data={
                'name': 'Test Policy',
                'description': 'Test Description',
                'rule_name_0': 'Test Rule',
                'rule_query_string_0': 'Test Query String',
                'rule_regex_0': 'Test Regex',
                'rule_severity_0': 'Test Severity',
            }
        )

        form.full_clean()
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.cleaned_data['rules']), 1)
        self.assertEqual(form.cleaned_data['rules'][0], rule_data)
