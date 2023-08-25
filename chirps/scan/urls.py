"""URLS for the scan application."""
from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='scan_dashboard'),
    path('<int:scan_id>/', views.view_scan_history, name='scan_history_view'),
    path('edit/<int:scan_id>/', views.edit, name='scan_edit'),
    path('run/<int:scan_run_id>/', views.view_scan_run, name='view_scan_run'),
    path('create/', views.create, name='scan_create'),
    path('finding/<int:finding_id>/', views.finding_detail, name='finding_detail'),
    path('status/<int:scan_run_id>/', views.status, name='scan_status'),
    path('asset_status/<int:scan_asset_id>/', views.asset_status, name='scan_asset_status'),
    path('findings/<int:scan_run_id>/', views.findings_count, name='scan_findings_count'),
    path('vcr/<int:scan_id>/', views.vcr_control, name='scan_vcr'),
    path('vcr_start/<int:scan_id>/', views.vcr_start, name='scan_vcr_start'),
    path('vcr_stop/<int:scan_id>/', views.vcr_stop, name='scan_vcr_stop'),
]
