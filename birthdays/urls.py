from django.urls import path
from .views import birthdays_list

urlpatterns = [
    path('birthdays/', birthdays_list, name='birthdays_list'),
]
