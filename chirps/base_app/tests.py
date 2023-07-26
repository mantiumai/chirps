"""Tests for the base application."""
from pathlib import Path

from django.test import TestCase
from policy.models import Policy

from .management.commands.initialize_app import Command

fixture_path = Path(__file__).parent.resolve() / Path('./fixtures/embedding')


class InitializeAppTests(TestCase):
    """Test the initialize_app management command"""

    def test_load_data_from_fixtures(self):
        """Test that data is loaded"""
        assert Policy.objects.count() == 0
        command = Command()
        path = '/embedding/fixtures/embedding'
        command.load_data_from_fixtures(path)

        # check that data was loaded
        assert Policy.objects.count() > 0
