"""Worker application views"""
import os

from django.http import JsonResponse
from requests import Request

from chirps.celery import app


def worker_status(request: Request) -> JsonResponse:
    """Get the status of the Celery worker"""
    celery_inspection = app.control.inspect()
    celery_statuses = celery_inspection.ping()

    is_celery_running = False
    if celery_statuses:
        is_celery_running = all(v['ok'] == 'pong' for v in celery_statuses.values())

    is_rabbit_running = os.system('rabbitmqctl ping') == 0

    service_statuses = {'celery': is_celery_running, 'rabbitmq': is_rabbit_running}

    if all(result is True for result in service_statuses.values()):
        status = 'green'
    else:
        status = 'red'

    return JsonResponse({'overall_status': status, 'service_statuses': service_statuses})
