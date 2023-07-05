from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='scan_dashboard'),
    path('create/', views.create, name='scan_create'),
    path('result/<int:result_id>/', views.result_detail, name='result_detail'),
    path('finding/<int:finding_id>/', views.finding_detail, name='finding_detail')
]
