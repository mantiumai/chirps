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

        self.test_string = 'Here is some employee information. The following {} is sensitive.'
    
    def test_ssn_pattern(self):  
        rule = self.rules.get(name='SSN')  
        pattern = re.compile(rule.regex_test)  
    
        valid_ssn_numbers = [  
            "123-45-6789",  
            "987-65-4321",  
            "001-23-4567",  
        ]  
    
        for ssn in valid_ssn_numbers:  
            test_string = self.test_string.format(ssn)
            self.assertIsNotNone(pattern.search(test_string), ssn)  
    
    def test_ssn_pattern_invalid(self):  
        rule = self.rules.get(name='SSN')  
        pattern = re.compile(rule.regex_test)  
    
        invalid_ssn_numbers = [  
            "123-45-678",  
            "987-65-432A",  
            "001-23-45 67",  
        ]  
    
        for ssn in invalid_ssn_numbers:  
            test_string = self.test_string.format(ssn)
            self.assertIsNone(pattern.search(test_string), ssn)  
    
    def test_address_pattern(self):  
        rule = self.rules.get(name='Address')  
        pattern = re.compile(rule.regex_test)  
    
        valid_addresses = [  
            "123 Main Street, Los Angeles, CA 90001",  
            "987 Elm Avenue, New York, NY 10001",  
            "001 Oak Court, San Francisco, CA 94102",  
        ]  
    
        for address in valid_addresses:  
            test_string = self.test_string.format(address)
            self.assertIsNotNone(pattern.search(test_string), address)

    def test_address_pattern_invalid(self):  
        rule = self.rules.get(name='Address')  
        pattern = re.compile(rule.regex_test)  
    
        invalid_addresses = [  
            "123 Main Street, Los Angeles, CA",  
            "987 Elm Avenue, New York 10001",  
            "001 Oak Court, San Francisco 94102",  
        ]  
    
        for address in invalid_addresses:  
            test_string = self.test_string.format(address)
            self.assertIsNone(pattern.search(test_string), address)  
  
    def test_credit_card_pattern(self):  
        rule = self.rules.get(name='Credit Card')  
        pattern = re.compile(rule.regex_test)  
    
        valid_credit_cards = [  
            "1234-5678-9012-3456",  
            "9876 5432 1098 7654",  
            "0011 2233 4455 6677",  
        ]  
    
        for credit_card in valid_credit_cards:
            test_string = self.test_string.format(credit_card)
            self.assertIsNotNone(pattern.search(test_string), credit_card)  
    
    def test_credit_card_pattern_invalid(self):  
        rule = self.rules.get(name='Credit Card')  
        pattern = re.compile(rule.regex_test)  
    
        invalid_credit_cards = [  
            "9876 5432",  
            "1234 5678 9012",  
            "0011 2233 4455 ABCD",  
        ]    
    
        for credit_card in invalid_credit_cards:  
            test_string = self.test_string.format(credit_card)
            self.assertIsNone(pattern.search(test_string), credit_card)  
  
    def test_email_address_pattern(self):  
        rule = self.rules.get(name='Email Address')  
        pattern = re.compile(rule.regex_test)  
    
        valid_email_addresses = [  
            "example@example.com",  
            "test.user@domain.co.uk",  
            "user+tag@example.org",  
        ]  
    
        for email_address in valid_email_addresses:  
            test_string = self.test_string.format(email_address)
            self.assertIsNotNone(pattern.search(test_string), email_address)  
    
    def test_email_address_pattern_invalid(self):  
        rule = self.rules.get(name='Email Address')  
        pattern = re.compile(rule.regex_test)  
    
        invalid_email_addresses = [  
            "example@example",  
            "test.user@domain",  
            "user+tag@example@org",  
        ]  
    
        for email_address in invalid_email_addresses:  
            test_string = self.test_string.format(email_address)
            self.assertIsNone(pattern.search(test_string), email_address)  
    
    def test_phone_number_pattern(self):  
        rule = self.rules.get(name='Phone number')  
        pattern = re.compile(rule.regex_test)  
    
        valid_phone_numbers = [  
            "123-456-7890",  
            "123.456.7890",  
            "(123) 456-7890",  
        ]  
    
        for phone_number in valid_phone_numbers:  
            test_string = self.test_string.format(phone_number)
            self.assertIsNotNone(pattern.search(test_string), phone_number)  
    
    def test_phone_number_pattern_invalid(self):  
        rule = self.rules.get(name='Phone number')  
        pattern = re.compile(rule.regex_test)  
    
        invalid_phone_numbers = [  
            "123-456-78",  
            "123.456.78A",  
            "(123) 45 67890",  
        ]  
    
        for phone_number in invalid_phone_numbers:  
            test_string = self.test_string.format(phone_number)
            self.assertIsNone(pattern.search(test_string), phone_number)  
  
    def test_salary_pattern(self):  
        rule = self.rules.get(name='Salary')  
        pattern = re.compile(rule.regex_test)  
    
        valid_salaries = [  
            "$1,000.00",  
            "$100,000",  
            "$1,234,567.89",  
        ]  
    
        for salary in valid_salaries:  
            test_string = self.test_string.format(salary)
            self.assertIsNotNone(pattern.search(test_string), salary)  

    def test_salary_pattern_invalid(self):  
        rule = self.rules.get(name='Salary')  
        pattern = re.compile(rule.regex_test)  
    
        invalid_salaries = [  
            "1,000.00",  
            "100,000",  
            "1,234,567.89",  
        ]  
    
        for salary in invalid_salaries:  
            test_string = self.test_string.format(salary)
            self.assertIsNone(pattern.search(test_string), salary)  


class NetworkSecurityRegexTests(TestCase):  
    """Test rule regex"""  
  
    fixtures = ['plan/network.json']  
  
    def setUp(self):  
        network_security_plan = Plan.objects.get(name="Network Security")  
        current_plan_version = network_security_plan.current_version  
        self.rules = Rule.objects.filter(plan=current_plan_version) 
        self.test_string = 'Here is some network security information. The following {} is sensitive.' 
  
    def test_open_ports_pattern(self):  
        rule = self.rules.get(name='Open Ports')  
        pattern = re.compile(rule.regex_test)  
  
        valid_ports = [  
            "80",  
            "443",  
            "22",  
        ]  
  
        for port in valid_ports:  
            test_string = self.test_string.format(port)
            self.assertIsNotNone(pattern.search(test_string), port)  
  
    def test_open_ports_pattern_invalid(self):  
        rule = self.rules.get(name='Open Ports')  
        pattern = re.compile(rule.regex_test)  
  
        invalid_ports = [  
            "65536",  
            "abcd",  
            "-1",  
        ]  
  
        for port in invalid_ports:  
            test_string = self.test_string.format(port)
            self.assertIsNone(pattern.search(test_string), port)  
  
    def test_firewall_configuration_pattern(self):  
        rule = self.rules.get(name='Firewall Configuration')  
        pattern = re.compile(rule.regex_test)  
    
        valid_firewall_rules = [  
            "allow from 192.168.1.1 to 10.0.0.1 port 80",  
            "deny from any to 10.0.0.2 port any",  
            "allow from 192.168.0.0 to any port 443",  
        ]  
    
        for firewall_rule in valid_firewall_rules:  
            test_string = self.test_string.format(firewall_rule)
            self.assertIsNotNone(pattern.search(test_string), firewall_rule)  
    
    def test_firewall_configuration_pattern_invalid(self):  
        rule = self.rules.get(name='Firewall Configuration')  
        pattern = re.compile(rule.regex_test)  
    
        invalid_firewall_rules = [  
            "allow from 192.168.1.1000 to 10.0.0.1 port 80",  
            "deny from any to 10.0.0.2",  
            "allow from 192.168.0.0 to any",  
        ]  
    
        for firewall_rule in invalid_firewall_rules:  
            test_string = self.test_string.format(firewall_rule)
            self.assertIsNone(pattern.search(test_string), firewall_rule)
    
    def test_network_encryption_pattern(self):  
        rule = self.rules.get(name='Network Encryption')  
        pattern = re.compile(rule.regex_test)  
  
        valid_encryptions = [  
            "none",  
            "WEP",  
            "WPA",  
            "WPA2",  
            "WPA3",  
        ]  
  
        for encryption in valid_encryptions:  
            test_string = self.test_string.format(encryption)
            self.assertIsNotNone(pattern.search(test_string), encryption)  
  
    def test_network_encryption_pattern_invalid(self):  
        rule = self.rules.get(name='Network Encryption')  
        pattern = re.compile(rule.regex_test)  
  
        invalid_encryptions = [  
            "WPA4",  
            "ABC",  
            "123",  
        ]  
  
        for encryption in invalid_encryptions:  
            test_string = self.test_string.format(encryption)
            self.assertIsNone(pattern.search(test_string), encryption)  
  
    def test_network_authentication_pattern(self):  
        rule = self.rules.get(name='Network Authentication')  
        pattern = re.compile(rule.regex_test)  
  
        valid_authentications = [  
            "WEP",  
            "WPA-PSK",  
            "WPA2-PSK",  
            "WPA3-PSK",  
            "WPA-Enterprise",  
            "WPA2-Enterprise",  
            "WPA3-Enterprise",  
        ]  
  
        for authentication in valid_authentications:  
            test_string = self.test_string.format(authentication)
            self.assertIsNotNone(pattern.search(test_string), authentication)  
  
    def test_network_authentication_pattern_invalid(self):  
        rule = self.rules.get(name='Network Authentication')  
        pattern = re.compile(rule.regex_test)  
  
        invalid_authentications = [  
            "WPA4-PSK",  
            "WPA1-Enterprise",  
            "ABC",  
            "123",  
        ]  
  
        for authentication in invalid_authentications: 
            test_string = self.test_string.format(authentication) 
            self.assertIsNone(pattern.search(test_string), authentication)  


class SensitiveDataRegexTests(TestCase):  
    """Test rule regex"""  
  
    fixtures = ['plan/sensitive_data.json']  
  
    def setUp(self):  
        sensitive_data_plan = Plan.objects.get(name="Sensitive Data")  
        current_plan_version = sensitive_data_plan.current_version  
        self.rules = Rule.objects.filter(plan=current_plan_version) 
        self.test_string = 'Here is some information. The following {} is sensitive.'  
  
    def test_credit_card_pattern(self):  
        rule = self.rules.get(name='Credit Card Numbers')  
        pattern = re.compile(rule.regex_test)  
  
        valid_credit_cards = [  
            "1234 5678 9012 3456",  
            "9876-5432-1098-7654",  
            "0011223344556677",  
        ]  
  
        for credit_card in valid_credit_cards:  
            test_string = self.test_string.format(credit_card)
            self.assertIsNotNone(pattern.search(test_string), credit_card)  
  
    def test_credit_card_pattern_invalid(self):  
        rule = self.rules.get(name='Credit Card Numbers')  
        pattern = re.compile(rule.regex_test)  
  
        invalid_credit_cards = [  
            "1234 5678 9012",  
            "9876-5432-1098 765A",  
            "001122334455 667",  
        ]  
  
        for credit_card in invalid_credit_cards:  
            test_string = self.test_string.format(credit_card)
            self.assertIsNone(pattern.search(test_string), credit_card)  
  
    def test_social_security_pattern(self):  
        rule = self.rules.get(name='Social Security Numbers')  
        pattern = re.compile(rule.regex_test)  
  
        valid_ssn_numbers = [  
            "123-45-6789",  
            "987 65 4321",  
            "001234567",  
        ]  
  
        for ssn in valid_ssn_numbers:  
            test_string = self.test_string.format(ssn)
            self.assertIsNotNone(pattern.search(test_string), ssn)  
  
    def test_social_security_pattern_invalid(self):  
        rule = self.rules.get(name='Social Security Numbers')  
        pattern = re.compile(rule.regex_test)  
  
        invalid_ssn_numbers = [  
            "123-45-678",  
            "987-65-432A",  
            "001-23-45 67",  
        ]  
  
        for ssn in invalid_ssn_numbers:  
            test_string = self.test_string.format(ssn)
            self.assertIsNone(pattern.search(test_string), ssn)  
  
    def test_bank_account_pattern(self):  
        rule = self.rules.get(name='Bank Account Numbers')  
        pattern = re.compile(rule.regex_test)  
  
        valid_bank_account_numbers = [  
            "1234567890",  
            "987654321098",  
            "001234567891",  
        ]  
  
        for bank_account_number in valid_bank_account_numbers:  
            test_string = self.test_string.format(bank_account_number)
            self.assertIsNotNone(pattern.search(test_string), bank_account_number)  
  
    def test_bank_account_pattern_invalid(self):  
        rule = self.rules.get(name='Bank Account Numbers')  
        pattern = re.compile(rule.regex_test)  
  
        invalid_bank_account_numbers = [  
            "123456789",  
            "9876543210987",  
            "00123456789A",  
        ]  
  
        for bank_account_number in invalid_bank_account_numbers:
            test_string = self.test_string.format(bank_account_number)  
            self.assertIsNone(pattern.search(test_string), bank_account_number)  
  
    def test_email_pattern(self):  
        rule = self.rules.get(name='Email Addresses')  
        pattern = re.compile(rule.regex_test)  
  
        valid_email_addresses = [  
            "example@example.com",  
            "test.user@domain.co.uk",  
            "user+tag@example.org",  
        ]  
  
        for email_address in valid_email_addresses:  
            test_string = self.test_string.format(email_address)
            self.assertIsNotNone(pattern.search(test_string), email_address)  
  
    def test_email_pattern_invalid(self):  
        rule = self.rules.get(name='Email Addresses')  
        pattern = re.compile(rule.regex_test)  
  
        invalid_email_addresses = [  
            "example@example",  
            "test.user@domain",  
            "user+tag@example@org",  
        ]  
  
        for email_address in invalid_email_addresses:  
            test_string = self.test_string.format(email_address)
            self.assertIsNone(pattern.search(test_string), email_address)  
  
    def test_phone_number_pattern(self):  
        rule = self.rules.get(name='Phone Numbers')  
        pattern = re.compile(rule.regex_test)  
  
        valid_phone_numbers = [  
            "123-456-7890",  
            "987-654-3210",  
            "555-123-4567",  
        ]  
  
        for phone_number in valid_phone_numbers:  
            test_string = self.test_string.format(phone_number)
            self.assertIsNotNone(pattern.search(test_string), phone_number)  
  
    def test_phone_number_pattern_invalid(self):  
        rule = self.rules.get(name='Phone Numbers')  
        pattern = re.compile(rule.regex_test)  
  
        invalid_phone_numbers = [  
            "123-45-6789",  
            "987-65-432A",  
            "001-23-45 67",  
        ]  
  
        for phone_number in invalid_phone_numbers:  
            test_string = self.test_string.format(phone_number)
            self.assertIsNone(pattern.search(test_string), phone_number)  
  
    def test_password_pattern(self):  
        rule = self.rules.get(name='Passwords')  
        pattern = re.compile(rule.regex_test)  
  
        valid_passwords = [  
            "password123!",  
            "Test@123",  
            "abc$%^789",  
        ]  
  
        for password in valid_passwords:  
            test_string = self.test_string.format(password)
            self.assertIsNotNone(pattern.search(test_string), password)  
  
    def test_password_pattern_invalid(self):  
        rule = self.rules.get(name='Passwords')  
        pattern = re.compile(rule.regex_test)  
  
        invalid_passwords = [  
            "   ",  
            "\n\t",  
        ]  
  
        for password in invalid_passwords:  
            test_string = self.test_string.format(password)
            self.assertIsNone(pattern.search(test_string), password)  


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
