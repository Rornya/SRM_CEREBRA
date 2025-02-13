from django.urls import path, include
from . import views
from attachments.views import upload_attachment
from observers import views as observer_views

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:project_id>/edit/', views.project_update, name='project_update'),
    path('project/<int:project_id>/upload/', upload_attachment, name='upload_project_attachment'),
    path('<int:project_id>/complete/', views.complete_project, name='complete_project'),  
    path('observers/', include('observers.urls')),
    path('observers/add_observer_to_project/<int:project_id>/', observer_views.add_observer_to_project, name='add_observer_to_project'),
    path('project/<int:project_id>/remove_participant/<int:participant_id>/', views.remove_participant, name='remove_participant'),
    path('delete/<int:project_id>/', views.delete_project, name='delete_project'),
    path('projects/<int:project_id>/extend_end_date/', views.extend_project_end_date, name='extend_project_end_date'),
    path('projects/<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('api/project/<int:project_id>/tasks/', views.project_tasks_api, name='project_tasks_api'),
]
