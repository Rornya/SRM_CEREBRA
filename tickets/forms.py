from django import forms
from .models import Ticket, TicketChatMessage
from assistants.models import Assistant  # Импортируем модель Assistant
from departments.models import Department 
from django.contrib.auth.models import User
from datetime import datetime
from users.models import UserProfile 

class TicketCreationForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all().order_by('name'),
        required=False,
        label="Выберите отдел",
        empty_label="Выберите отдел"
    )
    assignee = forms.ModelChoiceField(
        queryset=User.objects.none(),  # По умолчанию пустой QuerySet
        required=False,
        label="Исполнитель"
    )
    observers = forms.ModelChoiceField(
        queryset=UserProfile.objects.filter(full_statistics=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Наблюдатель"
    )

    def __init__(self, *args, **kwargs):
        super(TicketCreationForm, self).__init__(*args, **kwargs)
        # Фильтрация исполнителей по отделу
        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['assignee'].queryset = User.objects.filter(
                    userprofile__department_id=department_id
                ).select_related('userprofile').order_by('last_name')
            except (ValueError, TypeError):
                pass

        # Отображение ФИО в поле исполнителя
        self.fields['assignee'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline < datetime.now().date():
            raise forms.ValidationError("Нельзя создавать объекты с прошедшей датой.")
        return deadline

    class Meta:
        model = Ticket
        fields = ['title', 'description', 'department', 'assignee', 'observer', 'deadline']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date < timezone.now().date():
            raise forms.ValidationError("Нельзя создать заявку с прошедшей датой")
        return date

class AddAssistantForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        label="Выберите отдел",
        empty_label="Выберите отдел"
    )
    user = forms.ModelChoiceField(
        queryset=User.objects.none(),  # Пустой QuerySet для начального отображения
        label="Выберите ассистента",
        required=True  # Обязательно к заполнению
    )

    def __init__(self, *args, **kwargs):
        super(AddAssistantForm, self).__init__(*args, **kwargs)
        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['user'].queryset = User.objects.filter(
                    userprofile__department_id=department_id
                ).select_related('userprofile').order_by('last_name')
            except (ValueError, TypeError):
                pass

        # Переопределяем отображение ФИО для user
        self.fields['user'].label_from_instance = lambda obj: f"{obj.last_name} {obj.first_name}"

    class Meta:
        model = Assistant
        fields = ['department', 'user']

class TicketUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Переопределяем отображение пользователей в форме для ФИО
        self.fields['assignee'].queryset = User.objects.all()
        self.fields['assignee'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"
        #self.fields['observer'].queryset = User.objects.all()
        #self.fields['observer'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"

    class Meta:
        model = Ticket
        fields = ['title', 'description', 'assignee', 'deadline', 'status']  # Добавлено поле deadline
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

class TicketChatMessageForm(forms.ModelForm):
    class Meta:
        model = TicketChatMessage
        fields = ['message']
