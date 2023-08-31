"""worker application tests"""
from datetime import timedelta
from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import CeleryWorker


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

    @patch('worker.views.os')
    def test_worker_status_green(self, mock_os):
        """Test response when services are running"""
        # Make sure there's a worker that's available before we test
        CeleryWorker.objects.create(celery_name='Sir Testalot', available=True, last_success=timezone.now())

        # Mock the return call to querying RabbitMQ status
        mock_os.system.return_value = 0

        response = self.client.get('/worker/stats')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'btn-success')

    @patch('worker.views.os')
    def test_worker_status_red_bad_celery_worker(self, mock_os):
        """Test response when a Celery worker hasn't been reached in 20 minutes."""
        # Mock the return call to querying RabbitMQ status
        mock_os.system.return_value = 0

        # Make sure there's a worker that hasn't been available for a while
        CeleryWorker.objects.create(
            celery_name='Sir Testalot', available=True, last_success=timezone.now() - timedelta(minutes=20)
        )

        response = self.client.get('/worker/stats')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'btn-danger')

    @patch('worker.views.os')
    def test_worker_status_red_bad_rabbitmq(self, mock_os):
        """Test response when RabbitMQ is offline/"""
        # Mock the return call to querying RabbitMQ status
        mock_os.system.return_value = 1

        response = self.client.get('/worker/stats')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'btn-danger')
