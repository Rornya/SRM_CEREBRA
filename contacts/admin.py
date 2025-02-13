from django.contrib import admin
from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position', 'department', 'email')
    search_fields = ('full_name', 'email')
