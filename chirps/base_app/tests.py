"""Tests for the base application."""
from django.test import TestCase
from policy.models import Policy

from .management.commands.initialize_app import Command


class InitializeAppTests(TestCase):
    """Test the initialize_app management command"""

    def test_load_data_from_fixtures(self):
        """Test that data is loaded"""
        assert Policy.objects.count() == 0
        command = Command()
        command.load_data_from_fixtures()

        # check that data was loaded
        assert Policy.objects.count() > 0
