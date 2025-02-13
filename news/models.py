from django.db import models
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.utils import create_notification
from django.contrib.auth.models import User

class NewsPost(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news_posts')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    
    
    # Новые поля для фильтрации видимости
    is_visible_for_office = models.BooleanField(default=False, verbose_name='для Офиса')
    is_visible_for_warehouse = models.BooleanField(default=False, verbose_name='для Склада')
    is_visible_for_store = models.BooleanField(default=False, verbose_name='для Магазина')

    def get_absolute_url(self):
        return reverse('news_detail', args=[self.id])

    def __str__(self):
        return self.title

