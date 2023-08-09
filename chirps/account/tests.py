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
