from django import forms
from .models import Task, TaskChatMessage
from django.contrib.auth.models import User
from datetime import datetime
from users.models import UserProfile  # Импорт модели профиля

class TaskCreationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)  # Получаем переданный проект
        super(TaskCreationForm, self).__init__(*args, **kwargs)

        # Фильтрация пользователей для исполнителя - только участники проекта
        if project:
            self.fields['assignee'].queryset = User.objects.filter(participant__project=project)
        
        # Фильтрация пользователей для наблюдателей - только те, у кого включен full_statistics
        self.fields['observer'].queryset = User.objects.filter(userprofile__full_statistics=True)

        # Переопределяем отображение пользователей на ФИО
        self.fields['assignee'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"
        self.fields['observer'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline < datetime.now().date():
            raise forms.ValidationError("Нельзя создавать объекты с прошедшей датой.")
        return deadline

    def clean_assignee(self):
        assignee = self.cleaned_data.get('assignee')
        if not assignee:
            raise forms.ValidationError("Пожалуйста, выберите исполнителя для задачи. Если список пуст, добавьте сначала участников проекта")
        return assignee

    class Meta:
        model = Task
        fields = ['title', 'description', 'assignee', 'observer', 'deadline']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

class TaskUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)  # Получаем переданный проект
        super(TaskUpdateForm, self).__init__(*args, **kwargs)
        
        # Фильтрация пользователей только по участникам проекта
        if project:
            self.fields['assignee'].queryset = User.objects.filter(participant__project=project)
        
        # Фильтрация наблюдателей - только те, у кого включен full_statistics
        self.fields['observer'].queryset = User.objects.filter(userprofile__full_statistics=True)

        # Переопределяем отображение пользователей на ФИО
        self.fields['assignee'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"
        self.fields['observer'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline < datetime.now().date():
            raise forms.ValidationError("Нельзя устанавливать прошедшую дату для дедлайна.")
        return deadline

    def clean_assignee(self):
        assignee = self.cleaned_data.get('assignee')
        if not assignee:
            raise forms.ValidationError("Пожалуйста, выберите исполнителя для задачи. Если список пуст, добавьте сначала участников проекта")
        return assignee

    class Meta:
        model = Task
        fields = ['title', 'description', 'assignee', 'observer', 'deadline']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

class AddAssistantForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['assistant']

class TaskChatMessageForm(forms.ModelForm):
    class Meta:
        model = TaskChatMessage
        fields = ['message']
