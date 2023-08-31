"""Models for the worker application."""
from django.db import models


class CeleryWorker(models.Model):
    """Model to store state of a detected Celery worker."""

    celery_name = models.CharField(max_length=256)
    last_check = models.DateTimeField(auto_now_add=True)
    last_success = models.DateTimeField(null=True)
    available = models.BooleanField(default=False)
    active_jobs = models.IntegerField(default=0)

    def __str__(self):
        """Return the name of the Celery worker."""
        return self.celery_name
