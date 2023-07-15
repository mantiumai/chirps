"""Tests for the base application."""
from django.test import TestCase
from .management.commands.initialize_app import Command
from plan.models import Plan

class InitializeAppTests(TestCase):
    def test_load_data_from_plans_directory(self):
        assert Plan.objects.count() == 0
        command = Command()
        command.load_data_from_plans_directory()

        # check that data was loaded
        assert Plan.objects.count() > 0