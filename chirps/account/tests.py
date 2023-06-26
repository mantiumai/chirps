from django.contrib.auth.hashers import check_password, make_password
from django.test import TestCase

from .forms import ProfileForm


class AccountTests(TestCase):
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
