"""URLs for the policy app."""
from django.urls import path

from . import views

urlpatterns = [
    path('severity_management/create/', views.create_severity, name='create_severity'),
    path('severity_management/edit/<int:severity_id>/', views.edit_severity, name='edit_severity'),
    path('severity_management/archive/<int:severity_id>/', views.archive_severity, name='archive_severity'),
]
