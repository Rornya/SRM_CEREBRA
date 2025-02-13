from django.contrib import admin
from .models import Ticket

class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'assignee', 'status', 'created_at', 'closed_at')

admin.site.register(Ticket, TicketAdmin)
