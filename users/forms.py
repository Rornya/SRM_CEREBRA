from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['department']
        widgets = {
            'department': forms.TextInput(attrs={'class': 'form-control'}),
        }
