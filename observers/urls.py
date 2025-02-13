from django.urls import path
from . import views

urlpatterns = [
    path('add_observer_to_ticket/<int:ticket_id>/', views.add_observer_to_ticket, name='add_observer_to_ticket'),
    path('add_observer_to_task/<int:task_id>/', views.add_observer_to_task, name='add_observer_to_task'),
    path('add_observer_to_tectask/<int:tectask_id>/', views.add_observer_to_tectask, name='add_observer_to_tectask'),
    path('add_observer_to_project/<int:project_id>/', views.add_observer_to_project, name='add_observer_to_project'),
]
