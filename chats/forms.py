from django import forms
from .models import ProjectChatMessage

class ProjectChatMessageForm(forms.ModelForm):
    class Meta:
        model = ProjectChatMessage
        fields = ['message']
