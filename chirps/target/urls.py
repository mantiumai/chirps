"""URLs for the asset app."""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='asset_dashboard'),
    path('create/<str:html_name>', views.create, name='asset_create'),
    path('ping/<int:asset_id>/', views.ping, name='asset_ping'),
    path('delete/<int:asset_id>', views.delete, name='asset_delete'),
    path('decrypted_keys/', views.decrypted_keys, name='decrypted_keys'),
]
