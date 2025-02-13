from django.urls import path
from . import views

urlpatterns = [
    path('add/<int:project_id>/', views.add_participant_to_project, name='add_participant_to_project'),
]
