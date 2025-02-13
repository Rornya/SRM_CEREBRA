from django import forms
from .models import NewsPost

class NewsForm(forms.ModelForm):
    class Meta:
        model = NewsPost
        fields = ['title', 'content', 'is_visible_for_office', 'is_visible_for_warehouse', 'is_visible_for_store']

    def get_absolute_url(self):
        return reverse('news_detail', args=[self.id])  # Убедитесь, что здесь правильный отступ
