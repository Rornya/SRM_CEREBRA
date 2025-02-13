from django import forms
from .models import Activity
from profiles.models import UserProfile  # Замените на корректный путь, если требуется

class ActivityForm(forms.ModelForm):
    activity_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    activity_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    participants = forms.ModelMultipleChoiceField(
        queryset=UserProfile.objects.exclude(user__username="Ghost"),  # Исключаем пользователя Ghost
        widget=forms.CheckboxSelectMultiple,
        label="Участники"
    )

    class Meta:
        model = Activity
        fields = ['title', 'description', 'activity_date', 'activity_time', 'participants']
