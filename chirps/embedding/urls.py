"""URLs for the embedding app."""
from django.urls import path

from . import views

urlpatterns = [
    path('', views.show, name='embedding_list'),
    path('create/', views.create, name='embedding_create'),
    path('delete/<int:embedding_id>/', views.delete, name='embedding_delete'),
]
