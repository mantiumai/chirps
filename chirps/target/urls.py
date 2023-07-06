"""URLs for the target app."""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='target_dashboard'),
    path('create/<str:html_name>', views.create, name='target_create'),
    path('delete/<int:target_id>', views.delete, name='target_delete'),
    path('decrypted_keys/', views.decrypted_keys, name='decrypted_keys'),
]
