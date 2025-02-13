from django import forms
from .models import Assistant
from departments.models import Department
from django.contrib.auth.models import User

class AddAssistantForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all().order_by('name'),
        required=False,
        label="Выберите отдел",
        empty_label="Выберите отдел"
    )
    user = forms.ModelChoiceField(
        queryset=User.objects.none(),  # Пустой QuerySet для начального отображения
        label="Выберите ассистента",
        required=True  # Поле обязательно для заполнения
    )

    def __init__(self, *args, **kwargs):
        super(AddAssistantForm, self).__init__(*args, **kwargs)
        
        # Убедитесь, что данные передаются при обновлении списка ассистентов на основе отдела
        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['user'].queryset = User.objects.filter(
                    userprofile__department_id=department_id
                ).select_related('userprofile').order_by('last_name')
            except (ValueError, TypeError):
                self.fields['user'].queryset = User.objects.none()
        # Если форма не содержит данных, фильтруем только существующие ассистенты
        else:
            self.fields['user'].queryset = User.objects.none()

        # Отображение ФИО в поле user
        self.fields['user'].label_from_instance = lambda obj: f"{obj.last_name} {obj.first_name}"

    class Meta:
        model = Assistant
        fields = ['department', 'user']
