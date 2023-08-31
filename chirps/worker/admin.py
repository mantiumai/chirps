"""Registration point of the admin interface for the scan app."""
from django.contrib import admin

from .models import CeleryWorker

admin.site.register(CeleryWorker)
