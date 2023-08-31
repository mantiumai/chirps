"""Celery tasks for the worker application."""
from logging import getLogger
from typing import Any

from celery import Celery
from django.utils import timezone

from chirps.celery import app as celery_app

from .models import CeleryWorker

logger = getLogger(__name__)


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender: Celery, **kwargs: Any) -> None:
    """Register the ping task."""
    # Calls ping_task every 20 seconds - for some reason this period is always double what it's configured as
    sender.add_periodic_task(10.0, ping_task.s(), name='Celery Worker Ping')


@celery_app.task
def ping_task() -> None:
    """Query the Celery worker for its status."""
    celery_inspection = celery_app.control.inspect()   # type: ignore[attr-defined]
    celery_statuses = celery_inspection.active()

    # First pass: add any new workers and update existing workers
    for worker in celery_statuses.keys():
        worker_obj, _created = CeleryWorker.objects.get_or_create(celery_name=worker)
        worker_obj.last_success = timezone.now()
        worker_obj.available = True
        worker_obj.active_jobs = len(celery_statuses[worker])
        worker_obj.save()
