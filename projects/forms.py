from django import forms
from .models import Project, ProjectChatMessage
from django.contrib.auth.models import User
from datetime import datetime

class ProjectForm(forms.ModelForm):
    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')  # Проверка для поля end_date
        if end_date and end_date.date() < datetime.now().date():
            raise forms.ValidationError("Нельзя создавать Проекты с прошедшей датой.")
        return end_date

    class Meta:
        model = Project
        fields = ['title', 'description', 'end_date']
        labels = {
            'title': 'Название',
            'description': 'Описание',
        }
        widgets = {
            'end_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

class ProjectChatMessageForm(forms.ModelForm):
    class Meta:
        model = ProjectChatMessage
        fields = ['message']

class ProjectExtendEndDateForm(forms.ModelForm):
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Новая дата окончания")

    class Meta:
        model = Project
        fields = ['end_date']