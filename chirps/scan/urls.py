"""URLS for the scan application."""
from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='scan_dashboard'),
    path('<int:scan_id>/', views.view_scan, name='scan_view'),
    path('create/', views.create, name='scan_create'),
    path('result/<int:scan_id>/<int:policy_id>/<int:rule_id>/', views.result_detail, name='result_detail'),
    path('finding/<int:finding_id>/', views.finding_detail, name='finding_detail'),
    path('status/<int:scan_id>/', views.status, name='scan_status'),
    path('target_status/<int:scan_target_id>/', views.target_status, name='scan_target_status'),
    path('findings/<int:scan_id>/', views.findings_count, name='scan_findings_count'),
]
