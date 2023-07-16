"""Tests for the plan application."""

import re
from unittest import skip

from django.test import TestCase
from django.urls import reverse

from .forms import PlanForm
from .models import Plan, PlanVersion, Rule


class EmployeeRegexTests(TestCase):
    """Test rule regex"""

    fixtures = ['plan/employee.json']
    
    def setUp(self):
        # Query the Plan with the name "Employee Information"  
        employee_information_plan = Plan.objects.get(name="Employee Information")  
        
        # Get the current PlanVersion associated with the retrieved plan  
        current_plan_version = employee_information_plan.current_version  
        
        # Get all the rules associated with the current PlanVersion  
        self.rules = Rule.objects.filter(plan=current_plan_version)  
        
        # Print the retrieved rules  
        for rule in self.rules:  
            print(rule)  
  
    
    def test_social_security_number(self):  
        rule = self.rules.get(name='SSN')  
        pattern = re.compile(rule.regex_test)  
    
        example = 'this is a test. the number is 123-45-6789. the end!'  
        self.assertIsNotNone(pattern.search(example))  

    # def test_address(self):
    #     rule = self.rules.get(name='Address')
    #     pattern = re.compile(rule.regex_test)

    #     valid_addresses = [  
    #         # "123 Main St, CA 90210",  
    #         "456 Elm St, New York, NY 10001",  
    #         "789 Oak St, Los Angeles, CA 90001-1234",  
    #     ]  
  
    #     invalid_addresses = [  
    #         "12345 67890, NY 10001",  
    #         "Main St, CA 90210",  
    #         "123 Main St, California 90210",  
    #     ]  
    
    #     for address in valid_addresses:  
    #         self.assertIsNotNone(pattern.search(address), address)  
    
    #     for address in invalid_addresses:  
    #         self.assertIsNone(pattern.search(address), address)  

        
    #     example = "The address is 123 Main Street, Springfield, OH. That's the spot."
    #     self.assertIsNotNone(pattern.search(example))

    def test_bank_account_number(self):
        rule = self.rules.get(name='Bank Account')
        pattern = re.compile(rule.regex_test)

        valid_account_numbers = [  
            "123-4567-8901234",  
            "987-1234-5678901",  
            "001-0001-0000000",  
        ]

        for account_number in valid_account_numbers:  
            self.assertIsNotNone(pattern.match(account_number), account_number)


@skip('Disabling until pagination is re-added to the plan application.')
class PlanPaginationTests(TestCase):
    """Test the plan application pagination."""

    fixtures = ['plan/employee.json', 'plan/network.json', 'plan/sensitive_data.json']

    def setUp(self):
        """Login the user before performing any tests."""
        self.client.post(
            reverse('signup'),
            {'username': 'admin', 'email': 'admin@mantiumai.com', 'password1': 'admin', 'password2': 'admin'},
        )

    def test_dashboard_no_pagination(self):
        """Verify that no pagination widget is displayed when there are less than 25 items."""
        response = self.client.get(reverse('plan_dashboard'))

        # No pagination widget should be present
        # Ensure the element ID is not found
        self.assertNotContains(response, 'chirps-pagination-widget', status_code=200)

        # All 3 scans should be present (look for the element IDs)
        for scan_id in ['100', '200', '300']:
            self.assertContains(response, f'chirps-plan-{scan_id}', status_code=200)

    def test_dashboard_pagination(self):
        """Verify that the 3 pages are available and that the pagination widget is displayed."""
        # First page
        response = self.client.get(reverse('plan_dashboard'), {'item_count': 1})
        self.assertContains(response, 'chirps-pagination-widget', status_code=200)
        self.assertContains(response, 'chirps-plan-100', status_code=200)

        # Second page
        response = self.client.get(reverse('plan_dashboard'), {'item_count': 1, 'page': 2})
        self.assertContains(response, 'chirps-pagination-widget', status_code=200)
        self.assertContains(response, 'chirps-plan-200', status_code=200)

        # Third page
        response = self.client.get(reverse('plan_dashboard'), {'item_count': 1, 'page': 3})
        self.assertContains(response, 'chirps-pagination-widget', status_code=200)
        self.assertContains(response, 'chirps-plan-300', status_code=200)

    def test_dashboard_last_page(self):
        """If the page number exceeds the number of pages, verify that the last page is returned"""
        response = self.client.get(reverse('plan_dashboard'), {'item_count': 1, 'page': 100})
        self.assertContains(response, 'chirps-pagination-widget', status_code=200)
        self.assertContains(response, 'chirps-plan-300', status_code=200)


class PlanCreateForm(TestCase):
    """Test the custom logic in the plan create form."""

    def test_single_rule(self):
        """Verify that a single rule is parsed correctly."""
        rule_data = {
            'rule_name': 'Test Rule',
            'rule_query_string': 'Test Query String',
            'rule_regex': 'Test Regex',
            'rule_severity': 'Test Severity',
        }

        form = PlanForm(
            data={
                'name': 'Test Plan',
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
