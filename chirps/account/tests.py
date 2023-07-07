"""Tests for the account application."""
from django.test import TestCase
from django.urls import reverse

from .forms import ProfileForm


class AccountTests(TestCase):
    """Main test class for the account application."""

    def test_openai_key_hash(self):
        """Verify that the openai_key paramater is correctly hashed by the form"""
        secret_val = 'secret_12345abcd'
        form = ProfileForm({'openai_key': secret_val})

        # Valid form, or bust
        assert form.is_valid()

        # Make sure the password isn't part of the cleaned data!
        self.assertNotEqual(form.cleaned_data['openai_key'], secret_val)

        # Make sure the cleaned data is a valid hash
        self.assertTrue(form.cleaned_data['openai_key'].startswith('pbkdf2_sha256$'))

    def test_new_account_signup(self):
        """Verify that a new account can be created"""
        username = 'test_user'
        password = 'test_password'
        email = 'test_user@mantiumai.com'

        # Create a new account
        response = self.client.post(reverse('signup'), {
            'username': username,
            'email': email,
            'password1': password,
            'password2': password
        })
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
            }
        )
        self.assertRedirects(response, '/', status_code=302)
