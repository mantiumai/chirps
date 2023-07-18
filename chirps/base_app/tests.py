"""Tests for the base application."""
from django.test import TestCase
from policy.models import Plan

from .management.commands.initialize_app import Command


class InitializeAppTests(TestCase):
    """Test the initialize_app management command"""

    def test_load_data_from_plans_directory(self):
        """Test that data is loaded"""
        assert Plan.objects.count() == 0
        command = Command()
        command.load_data_from_plans_directory()

        # check that data was loaded
        assert Plan.objects.count() > 0
