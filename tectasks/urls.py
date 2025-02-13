from django.urls import path, include
from . import views
from assistants.views import add_assistant
from attachments.views import upload_attachment
from observers import views as observer_views

urlpatterns = [
    path('create/', views.tectask_create, name='tectask_create'),
    path('<int:tectask_id>/', views.tectask_detail, name='tectask_detail'),
     path('add_assistant/<str:object_type>/<int:object_id>/', add_assistant, name='add_assistant'),
    path('<int:tectask_id>/update/', views.tectask_update, name='tectask_update'),
    path('tectasks/', views.tectask_list, name='tectask_list'),
    path('tectask/<int:tectask_id>/return/', views.tectask_return_for_revision, name='tectask_return_for_revision'),
    path('tectask/<int:tectask_id>/upload/', upload_attachment, name='upload_tectask_attachment'),
    path('tectask/<int:tectask_id>/accept/', views.accept_tectask, name='accept_tectask'),
    path('tectask/<int:tectask_id>/complete/', views.complete_tectask, name='complete_tectask'),
    path('tectask/<int:tectask_id>/request_extension/', views.request_extension_tectask, name='request_extension_tectask'),
    path('observers/', include('observers.urls')),
    path('observers/add_observer_to_tectask/<int:tectask_id>/', observer_views.add_observer_to_tectask, name='add_observer_to_tectask'),
]
