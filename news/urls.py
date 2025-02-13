from django.urls import path
from . import views

urlpatterns = [
    path('', views.news_list, name='news_list'),
    path('<int:news_id>/', views.news_detail, name='news_detail'),
    path('add/', views.add_news, name='add_news'),  # Маршрут для добавления новостей
    path('edit/<int:news_id>/', views.edit_news, name='edit_news'),  # Маршрут для редактирования новостей
]
