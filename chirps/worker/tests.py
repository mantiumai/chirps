"""worker application tests"""
from unittest.mock import patch

from django.test import Client, TestCase


class WorkerStatusViewTests(TestCase):
    """Tests of the worker status view"""

    def setUp(self):
        """Test setup"""
        self.client = Client()

    @patch('worker.views.app')
    @patch('worker.views.os')
    def test_worker_status_green(self, mock_os, mock_app):
        """Test response when services are running"""
        # Mock the Celery worker and RabbitMQ statuses to be running
        mock_app.control.inspect.return_value.ping.return_value = {'worker1': {'ok': 'pong'}}
        mock_os.system.return_value = 0

        response = self.client.get('/worker/status/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {'overall_status': 'green', 'service_statuses': {'celery': True, 'rabbitmq': True}}
        )

    @patch('worker.views.app')
    @patch('worker.views.os')
    def test_worker_status_red(self, mock_os, mock_app):
        """Test response when services are not running"""
        # Mock the Celery worker and RabbitMQ statuses to be not running
        mock_app.control.inspect.return_value.ping.return_value = None
        mock_os.system.return_value = 1

        response = self.client.get('/worker/status/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {'overall_status': 'red', 'service_statuses': {'celery': False, 'rabbitmq': False}}
        )
