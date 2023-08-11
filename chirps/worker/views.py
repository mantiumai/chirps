from django.http import HttpResponse

from chirps.celery import app


def worker_status(request):
    """Get the worker's status"""
    inspection = app.control.inspect()  # Use app.control.inspect() instead of app.inspect()
    result = inspection.ping()

    if result:
        color = 'green'
    else:
        color = 'red'

    return HttpResponse(
        f'<div style="display: inline-block; width: 15px; height: 15px; border-radius: 50%; background-color: {color};"></div>'
    )
