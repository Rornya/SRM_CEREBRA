from django import forms
from .models import Observer

class ObserverForm(forms.ModelForm):
    class Meta:
        model = Observer
        fields = ['user']
