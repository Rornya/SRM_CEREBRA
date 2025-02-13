from django.urls import path
from . import views
from .views import statistics_view, employee_load_view  # Убедись, что импортировал employee_load_view

urlpatterns = [
    path('statistics/', views.statistics_view, name='statistics'),
    path('statistics/user/<int:employee_id>/', views.employee_load_view, name='employee_load'),
    path('statistics/departments/', views.department_statistics, name='department_statistics'),
    path('statistics/departments/<int:department_id>/', views.department_employee_statistics, name='department_employee_statistics'),
    path('statistics/employee/<int:employee_id>/', views.employee_statistics, name='employee_statistics'),
]
