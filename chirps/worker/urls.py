"""Worker application URLs"""
from django.urls import path

from . import views

urlpatterns = [
    path('stats', views.worker_status, name='worker_status'),
    path('status_details', views.status_details, name='worker_status_details'),
]
