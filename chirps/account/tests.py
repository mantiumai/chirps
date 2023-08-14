"""Tests for the account application."""
from django.test import TestCase
from django.urls import reverse


class AccountTests(TestCase):
    """Main test class for the account application."""

    def test_new_account_signup(self):
        """Verify that a new account can be created"""
        username = 'test_user'
        password = 'test_password'
        email = 'test_user@mantiumai.com'

        # Create a new account
        response = self.client.post(
            reverse('signup'), {'username': username, 'email': email, 'password1': password, 'password2': password}
        )
        self.assertRedirects(response, '/', 302)

        # Logout (since the account creation )
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'), 302)

        # Login (again)
        response = self.client.post(
            reverse('login'),
            {
                'username': username,
                'password': password,
            },
        )
        self.assertRedirects(response, '/', status_code=302)

    def test_password_change(self):
        """Verify that a password can be changed"""
        username = 'test_user'
        password = 'test_password'
        email = 'test_user@mantiumai.com'

        # Create a new account
        response = self.client.post(
            reverse('signup'), {'username': username, 'email': email, 'password1': password, 'password2': password}
        )
        self.assertRedirects(response, '/', 302)

        # Change the password
        new_password = 'new_password'
        response = self.client.post(
            reverse('change_password'),
            {
                'old_password': password,
                'new_password1': new_password,
                'new_password2': new_password,
            },
        )
        self.assertRedirects(response, reverse('profile'), status_code=302)

        # Login using the old password (should fail)
        response = self.client.post(
            reverse('login'),
            {
                'username': username,
                'password': password,
            },
        )
        self.assertEqual(response.status_code, 200)

        # Login using the new password (should succeed)
        response = self.client.post(
            reverse('login'),
            {
                'username': username,
                'password': new_password,
            },
        )
        self.assertRedirects(response, '/', status_code=302)
    
    def test_password_change_validation(self):
        """Verify that a password is validated when changed"""
        username = 'test_user'
        password = 'test_password'
        email = 'test_user@mantiumai.com'

        # Create a new account
        response = self.client.post(
            reverse('signup'), {'username': username, 'email': email, 'password1': password, 'password2': password}
        )
        self.assertRedirects(response, '/', 302)

        # Old password is incorrect
        new_password = 'new_password'
        response = self.client.post(
            reverse('change_password'),
            {
                'old_password': 'incorrect_password',
                'new_password1': new_password,
                'new_password2': new_password,
            },
        )
        self.assertEqual(response.status_code, 200)

        # New passwords do not match
        response = self.client.post(
            reverse('change_password'),
            {
                'old_password': password,
                'new_password1': new_password,
                'new_password2': 'incorrect_password',
            },
        )
        self.assertEqual(response.status_code, 200)

        # New password is too short
        response = self.client.post(
            reverse('change_password'),
            {
                'old_password': password,
                'new_password1': 'short',
                'new_password2': 'short',
            },
        )
        self.assertEqual(response.status_code, 200)

        # New password is entirely numeric
        response = self.client.post(
            reverse('change_password'),
            {
                'old_password': password,
                'new_password1': '98415651658',
                'new_password2': '98415651658',
            },
        )
        self.assertEqual(response.status_code, 200)
