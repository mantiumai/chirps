"""URLs for the plan app."""
from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='plan_dashboard'),
    path('archive/<int:plan_id>', views.archive, name='plan_archive'),
    path('clone/<int:plan_id>', views.clone, name='plan_clone'),
    path('create/', views.create, name='plan_create'),
    path('create_rule/', views.create_rule, name='plan_create_rule'),
    path('delete_rule/<int:rule_id>', views.delete_rule, name='plan_delete_rule'),
    path('edit/<int:plan_id>', views.edit, name='plan_edit'),
]
