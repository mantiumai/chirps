"""Worker application views"""
import os
from dataclasses import dataclass

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from chirps.celery import app


@dataclass
class ServiceStatus:
    """Helper model for the status of a services across the application."""

    status: str
    celery_status: bool
    rabbitmq_status: bool
    job_count: int


@login_required
def status(request: HttpRequest) -> HttpResponse:
    """Return the status widget."""
    return render(request, 'worker/status.html', {'service_status': _get_service_status()})


@login_required
def status_details(request: HttpRequest) -> HttpResponse:
    """Fetch the status details modal."""
    return render(request, 'worker/status_modal.html', {'service_status': _get_service_status()})


def _get_service_status() -> ServiceStatus:
    celery_inspection = app.control.inspect()   # type: ignore
    celery_statuses = celery_inspection.ping()

    is_celery_running = False
    if celery_statuses:
        is_celery_running = all(v['ok'] == 'pong' for v in celery_statuses.values())

    # Check how many Celery jobs are running
    job_count = 0
    if is_celery_running:
        workers = celery_inspection.active()

        # Shape of the workers dictionary is {worker_name: [list of jobs]}
        job_count = sum([len(jobs) for jobs in workers.values()])

    is_rabbit_running = os.system('rabbitmqctl ping') == 0

    if all(result is True for result in [is_celery_running, is_rabbit_running]):
        status = 'green'
    else:
        status = 'red'

    return ServiceStatus(
        celery_status=is_celery_running, rabbitmq_status=is_rabbit_running, status=status, job_count=job_count
    )
