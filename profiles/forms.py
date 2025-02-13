from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'position', 'department', 'internal_phone', 'mobile_phone', 'email', 'profile_photo', 'birthday', 'hire_date']
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'birthday': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }