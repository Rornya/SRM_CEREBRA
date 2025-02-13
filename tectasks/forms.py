from django import forms
from .models import Tectask, TectaskChatMessage
from assistants.models import Assistant  # Импортируем модель Assistant
from departments.models import Department
from django.contrib.auth.models import User
from datetime import datetime
from users.models import UserProfile

class TectaskCreationForm(forms.ModelForm):
    department = forms.ModelChoiceField(queryset=UserProfile.objects.none(), required=False, label="Отдел")
    assignee = forms.ModelChoiceField(queryset=User.objects.none(), required=False, label="Исполнитель")
    observers = forms.ModelMultipleChoiceField(
        queryset=UserProfile.objects.filter(full_statistics=True),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label="Наблюдатели"
    )

    class Meta:
        model = Tectask
        fields = ['title', 'description', 'department', 'assignee', 'observers', 'deadline']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        department_id = kwargs.pop('department_id', None)
        super().__init__(*args, **kwargs)
        
        # Фильтрация исполнителей по отделу, если указан department_id
        if department_id:
            self.fields['assignee'].queryset = UserProfile.objects.filter(department__id=department_id)
        else:
            self.fields['assignee'].queryset = UserProfile.objects.none()

        # Переопределяем отображение пользователей для ФИО
        self.fields['assignee'].label_from_instance = lambda obj: f"{obj.user.first_name} {obj.user.last_name}"
        self.fields['observers'].label_from_instance = lambda obj: f"{obj.user.first_name} {obj.user.last_name}"

class AddAssistantForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        label="Выберите отдел",
        empty_label="Выберите отдел"
    )
    user = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label="Выберите ассистента",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Assistant
        fields = ['department', 'user']

    def __init__(self, *args, **kwargs):
        super(AddAssistantForm, self).__init__(*args, **kwargs)
        # Фильтрация сотрудников по отделу при загрузке формы или изменении отдела
        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['user'].queryset = User.objects.filter(
                    userprofile__department_id=department_id
                ).order_by('last_name')
            except (ValueError, TypeError):
                pass
        else:
            self.fields['user'].queryset = User.objects.none()

        # Отображение ФИО в выпадающем списке
        self.fields['user'].label_from_instance = lambda obj: f"{obj.last_name} {obj.first_name}"


class TectaskUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Переопределяем отображение пользователей в форме для ФИО
        self.fields['assignee'].queryset = User.objects.all()
        self.fields['assignee'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"
        self.fields['observer'].queryset = User.objects.all()
        self.fields['observer'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"

    class Meta:
        model = Tectask
        fields = ['title', 'description', 'assignee', 'observer', 'status']


class TectaskChatMessageForm(forms.ModelForm):
    class Meta:
        model = TectaskChatMessage
        fields = ['message']
