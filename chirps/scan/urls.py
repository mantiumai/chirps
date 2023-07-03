from django.urls import path

from . import views

urlpatterns = [  
    path('', views.dashboard, name='scan_dashboard'),  
    path('create/', views.create, name='scan_create'),  
    path('result_details/<int:result_id>/', views.result_details, name='result_details'),  
]  