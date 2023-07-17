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
    
    def test_ssn_pattern(self):  
        rule = self.rules.get(name='SSN')  
        pattern = re.compile(rule.regex_test)  
    
        valid_ssn_numbers = [  
            "123-45-6789",  
            "987-65-4321",  
            "001-23-4567",  
        ]  
    
        for ssn_number in valid_ssn_numbers:  
            self.assertIsNotNone(pattern.match(ssn_number), ssn_number)  
    
    def test_address_pattern(self):  
        rule = self.rules.get(name='Address')  
        pattern = re.compile(rule.regex_test)  
    
        valid_addresses = [  
            "123 Main Street, Los Angeles, CA 90001",  
            "987 Elm Avenue, New York, NY 10001",  
            "001 Oak Court, San Francisco, CA 94102",  
        ]  
    
        for address in valid_addresses:  
            self.assertIsNotNone(pattern.match(address), address)  
    
    def test_credit_card_pattern(self):  
        rule = self.rules.get(name='Credit Card')  
        pattern = re.compile(rule.regex_test)  
    
        valid_credit_cards = [  
            "1234 5678 9012 3456",  
            "9876 5432 1098 7654",  
            "0011 2233 4455 6677",  
        ]  
    
        for credit_card in valid_credit_cards:  
            self.assertIsNotNone(pattern.match(credit_card), credit_card)  
    
    def test_email_address_pattern(self):  
        rule = self.rules.get(name='Email Address')  
        pattern = re.compile(rule.regex_test)  
    
        valid_email_addresses = [  
            "example@example.com",  
            "test.user@domain.co.uk",  
            "user+tag@example.org",  
        ]  
    
        for email_address in valid_email_addresses:  
            self.assertIsNotNone(pattern.match(email_address), email_address)  
    
    def test_phone_number_pattern(self):  
        rule = self.rules.get(name='Phone number')  
        pattern = re.compile(rule.regex_test)  
    
        valid_phone_numbers = [  
            "123-456-7890",  
            "123.456.7890",  
            "(123) 456-7890",  
        ]  
    
        for phone_number in valid_phone_numbers:  
            self.assertIsNotNone(pattern.match(phone_number), phone_number)  
    
    def test_salary_pattern(self):  
        rule = self.rules.get(name='Salary')  
        pattern = re.compile(rule.regex_test)  
    
        valid_salaries = [  
            "$1,000.00",  
            "$100,000",  
            "$1,234,567.89",  
        ]  
    
        for salary in valid_salaries:  
            self.assertIsNotNone(pattern.match(salary), salary)  


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
