"""worker application tests"""
from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse


class WorkerStatusViewTests(TestCase):
    """Tests of the worker status view"""

    def setUp(self):
        """Test setup"""
        self.client = Client()

        # Create a dummy user and login
        username = 'test_user'
        password = 'test_password'
        email = 'test_user@mantiumai.com'

        # Create a new account
        self.client.post(
            reverse('signup'), {'username': username, 'email': email, 'password1': password, 'password2': password}
        )

    @patch('worker.views.app')
    @patch('worker.views.os')
    def test_worker_status_green(self, mock_os, mock_app):
        """Test response when services are running"""
        # Mock the Celery worker, RabbitMQ, and Redis statuses to be running
        mock_app.control.inspect.return_value.ping.return_value = {'worker1': {'ok': 'pong'}}
        mock_os.system.return_value = 0

        response = self.client.get('/worker/status/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'btn-success')

    @patch('worker.views.app')
    @patch('worker.views.os')
    def test_worker_status_red(self, mock_os, mock_app):
        """Test response when services are not running"""
        # Mock the Celery worker, RabbitMQ, and Redis statuses to be not running
        mock_app.control.inspect.return_value.ping.return_value = None
        mock_os.system.return_value = 1

        response = self.client.get('/worker/status/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'btn-danger')
