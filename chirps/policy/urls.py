"""URLs for the policy app."""
from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='policy_dashboard'),
    path('archive/<int:policy_id>', views.archive, name='policy_archive'),
    path('clone/<int:policy_id>', views.clone, name='policy_clone'),
    path('create/', views.create, name='policy_create'),
    path('create_rule/', views.create_rule, name='policy_create_rule'),
    path('delete_rule/<int:rule_id>', views.delete_rule, name='policy_delete_rule'),
    path('edit/<int:policy_id>', views.edit, name='policy_edit'),
    path('severity_management/create/', views.create_severity, name='create_severity'),
    path('severity_management/edit/<int:severity_id>/', views.edit_severity, name='edit_severity'),
    path('severity_management/archive/<int:severity_id>/', views.archive_severity, name='archive_severity'),
]
