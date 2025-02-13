from django import forms
from django.contrib.auth.models import User
from .models import Participant

class AddParticipantsForm(forms.Form):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,  # Используем чекбоксы для отображения
        label="Выберите участников"
    )

    def __init__(self, *args, **kwargs):
        department = kwargs.pop('department', None)  # Получаем ID отдела
        super().__init__(*args, **kwargs)
        if department:
            self.fields['users'].queryset = User.objects.filter(userprofile__department_id=department)
        else:
            self.fields['users'].queryset = User.objects.none()  # Если отдел не выбран, пустой список
