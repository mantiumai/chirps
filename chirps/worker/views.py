from django.http import JsonResponse

from chirps.celery import app


def worker_status(request):
    """Get the status of the Celery worker"""
    inspection = app.control.inspect()
    result = inspection.ping()

    if result:
        status = 'green'
    else:
        status = 'red'

    return JsonResponse({'status': status})
