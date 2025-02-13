from django.contrib import admin
from .models import Attachment

class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_by', 'uploaded_at', 'task', 'ticket')

admin.site.register(Attachment, AttachmentAdmin)
