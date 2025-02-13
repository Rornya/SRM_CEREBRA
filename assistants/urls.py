from django.urls import path
from . import views

urlpatterns = [
    path('add_assistant/<str:object_type>/<int:object_id>/', views.add_assistant, name='add_assistant'),
    path('remove_assistant/<str:object_type>/<int:object_id>/<int:assistant_id>/', views.remove_assistant, name='remove_assistant'),
]
