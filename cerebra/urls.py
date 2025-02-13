from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from .views import home
from .views import gantt_view
from .views import birthdays_list
from django.utils.translation import gettext_lazy as _
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('news/', include('news.urls')),
    path('', home, name='home'),  # Главная страница
    path('projects/', include('projects.urls')),
    path('tasks/', include('tasks.urls')),
    path('tickets/', include('tickets.urls')),
    path('assistants/', include('assistants.urls')),
    path('participants/', include('participants.urls')),
    path('profiles/', include('profiles.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logged_out.html'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('stats/', include('stats.urls')),
    path('contacts/', include('contacts.urls')),
    path('calendars/', include('calendars.urls')),
    path('diary/', include('diary.urls')),
    path('tectasks/', include('tectasks.urls')),
    path('calendar/day/<str:date>/', views.day_view, name='day_view'),
    path('birthdays/', include('birthdays.urls')),  # Исправляем подключение birthdays
    path('activities/', include('activities.urls')),
    path('gantt/', gantt_view, name='gantt_view'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),
    path('gantt/fullscreen/', views.gantt_fullscreen_view, name='gantt_fullscreen'),
]


# Обслуживание медиа и статических файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
