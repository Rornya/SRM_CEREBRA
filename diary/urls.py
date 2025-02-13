from django.urls import path
from . import views

urlpatterns = [
    path('', views.diary_list, name='diary_list'),
    path('create/', views.diary_entry_create, name='diary_entry_create'),
    path('<int:entry_id>/', views.diary_entry_detail, name='diary_entry_detail'),
    path('entry/<int:pk>/complete/', views.mark_completed, name='diary_entry_complete'),
    path('entry/<int:pk>/delete/', views.delete_entry, name='diary_entry_delete'),
]
