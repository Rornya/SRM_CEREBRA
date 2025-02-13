from django.urls import path, include
from . import views
from assistants.views import add_assistant
from attachments.views import upload_attachment
from observers import views as observer_views

urlpatterns = [
    path('create/', views.ticket_create, name='ticket_create'),
    path('<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('add_assistant/<str:object_type>/<int:object_id>/', add_assistant, name='add_assistant'),
    path('<int:ticket_id>/update/', views.ticket_update, name='ticket_update'),
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('ticket/<int:ticket_id>/return/', views.ticket_return_for_revision, name='ticket_return_for_revision'),
    path('ticket/<int:ticket_id>/upload/', upload_attachment, name='upload_ticket_attachment'),\
    path('ticket/<int:ticket_id>/accept/', views.accept_ticket, name='accept_ticket'),
    path('ticket/<int:ticket_id>/complete/', views.complete_ticket, name='complete_ticket'),
    path('ticket/<int:ticket_id>/request_extension/', views.request_extension_ticket, name='request_extension_ticket'),
    path('observers/', include('observers.urls')),
    path('observers/add_observer_to_ticket/<int:ticket_id>/', observer_views.add_observer_to_ticket, name='add_observer_to_ticket'),
    path('delete/<int:ticket_id>/', views.delete_ticket, name='delete_ticket'),
    path('tickets/', views.ticket_list, name='tickets_list'),
    path('tickets/<int:ticket_id>/edit/', views.edit_ticket, name='edit_ticket'),
]
