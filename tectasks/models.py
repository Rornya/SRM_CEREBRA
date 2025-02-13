from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Tectask(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),  
        ('in_progress', 'В процессе'),  
        ('extension_requested', 'Запрос на продление'),  
        ('done', 'Выполнена'),  
        ('completed', 'Завершена'), 
        ('in_revision', 'Отправлена на доработку'),
    ]

    title = models.CharField(max_length=255, verbose_name="Название задачи")
    description = models.TextField(verbose_name="Описание задачи", blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tectasks', verbose_name="Автор задачи", null=True, blank=True)
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tectasks', verbose_name="Исполнитель", null=True, blank=True)
    observer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='observed_tectasks', verbose_name="Наблюдатель")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Статус задачи", default='new')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    accepted_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата принятия")
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата закрытия")
    return_count = models.IntegerField(default=0, verbose_name="Количество возвратов на доработку")
    deadline = models.DateField()
    
    # Поле для хранения ассистентов
    assistants = models.ManyToManyField(User, related_name="tectask_assistants", blank=True)

    def save(self, *args, **kwargs):
        if self.deadline and self.deadline < timezone.now().date():
            raise ValueError("Нельзя сохранять объекты с прошедшей датой.")
        if not self.deadline:  # Если дедлайн не указан, добавляем 3 дня
            self.deadline = timezone.now() + timedelta(days=3)
        super(Tectask, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class TectaskChatMessage(models.Model):
    tectask = models.ForeignKey(Tectask, on_delete=models.CASCADE, related_name='chat_messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.user} on {self.created_at}"
