"""URLs for the policy app."""
from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='policy_dashboard'),
    path('archive/<int:policy_id>', views.archive, name='policy_archive'),
    path('clone/<int:policy_id>', views.clone, name='policy_clone'),
    path('create/', views.create, name='policy_create'),
    path('create_rule/<str:rule_type>/', views.create_rule, name='policy_create_rule'),
    path('get_model_names/<str:selected_service>/', views.get_model_names, name='get_model_names'),
    path('delete_rule/<int:rule_id>', views.delete_rule, name='policy_delete_rule'),
    path('edit/<int:policy_id>', views.edit, name='policy_edit'),
    path('finding/<int:finding_id>/', views.finding_detail, name='finding_detail'),
]
