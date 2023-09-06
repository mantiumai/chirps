"""Worker application views"""
import os
from dataclasses import dataclass
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.cache import never_cache

from .models import CeleryWorker


@dataclass
class ServiceStatus:
    """Helper model for the status of a services across the application."""

    status: str
    celery_status: bool
    rabbitmq_status: bool
    job_count: int


@login_required
@never_cache
def worker_status(request: HttpRequest) -> HttpResponse:
    """Return the status widget."""
    return render(request, 'worker/status.html', {'service_status': _get_service_status()})


@login_required
@never_cache
def status_details(request: HttpRequest) -> HttpResponse:
    """Fetch the status details modal."""
    return render(request, 'worker/status_modal.html', {'service_status': _get_service_status()})


def _get_service_status() -> ServiceStatus:

    is_celery_running = True
    for celery_worker in CeleryWorker.objects.all():
        if celery_worker.available is False:
            is_celery_running = False
            break

        if celery_worker.last_success < timezone.now() - timedelta(minutes=1):
            is_celery_running = False
            break

    if CeleryWorker.objects.count() == 0:
        is_celery_running = False

    # Check how many Celery jobs are running
    job_count = CeleryWorker.objects.all().aggregate(models.Sum('active_jobs'))['active_jobs__sum']

    is_rabbit_running = os.system('rabbitmqctl ping') == 0

    if all(result is True for result in [is_celery_running, is_rabbit_running]):
        service_status = 'green'
    else:
        service_status = 'red'

    return ServiceStatus(
        celery_status=is_celery_running, rabbitmq_status=is_rabbit_running, status=service_status, job_count=job_count
    )
