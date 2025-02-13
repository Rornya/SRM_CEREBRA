# activities/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.activity_list, name='activity_list'),
    path('create/', views.activity_create, name='activity_create'),
    path('<int:pk>/complete/', views.activity_complete, name='activity_complete'),
    path('<int:pk>/delete/', views.activity_delete, name='activity_delete'),
    path('activities/<int:pk>/', views.activity_detail, name='activity_detail'),
]
