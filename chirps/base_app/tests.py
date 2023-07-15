"""Tests for the base application."""
from django.test import TestCase
from .management.commands.initialize_app import Command

class InitializeAppTests(TestCase):
    def test_load_data_from_plans_directory(self):
        command = Command()
        command.load_data_from_plans_directory()