from django.urls import path, include
from . import views
from assistants.views import add_assistant
from attachments.views import upload_attachment
from observers import views as observer_views

urlpatterns = [
    path('project/<int:project_id>/tasks/', views.task_list, name='task_list'),
    path('project/<int:project_id>/tasks/create/', views.task_create, name='task_create'),
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),
    path('task/<int:task_id>/update/', views.task_update, name='task_update'),
    path('task/<int:task_id>/return/', views.task_return_for_revision, name='task_return_for_revision'),
    path('task/<int:task_id>/upload/', upload_attachment, name='upload_task_attachment'),
    path('task/<int:task_id>/accept/', views.accept_task, name='accept_task'),
    path('task/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('task/<int:task_id>/request_extension/', views.request_extension_task, name='request_extension_task'),
    path('task/<int:task_id>/approve/', views.approve_task, name='approve_task'),
    path('task/<int:task_id>/reject/', views.reject_task, name='reject_task'),
    path('tasks/delete/<int:task_id>/', views.delete_task, name='delete_task'),
    
    # Исправленный маршрут для добавления ассистентов
    path('add_assistant/<str:object_type>/<int:object_id>/', add_assistant, name='add_assistant'),

    # Исправленный маршрут для добавления наблюдателей
    path('task/<int:task_id>/add_observer/', observer_views.add_observer_to_task, name='add_observer_to_task'),
    path('tasks/<int:task_id>/edit/', views.edit_task, name='edit_task'),
]
