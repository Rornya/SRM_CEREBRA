from django import forms
from .models import DiaryEntry
from datetime import datetime

class DiaryEntryForm(forms.ModelForm):
    def clean_entry_date(self):
        entry_date = self.cleaned_data.get('entry_date')
        if entry_date and entry_date < datetime.now().date():
            raise forms.ValidationError("Нельзя создавать объекты с прошедшей датой.")
        return entry_date

    class Meta:
        model = DiaryEntry
        fields = ['title', 'content', 'entry_date']
        widgets = {
            'entry_date': forms.DateInput(attrs={'type': 'date'}),
        }
