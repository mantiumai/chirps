from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='plan_dashboard'),
    path('create/', views.create, name='plan_create'),
]
