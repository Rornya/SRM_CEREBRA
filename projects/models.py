from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, date

class Project(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('in_progress', 'В процессе'),
        ('completed', 'Завершенный'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(default='', verbose_name="Описание проекта")
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    end_date = models.DateTimeField(null=True, blank=True , verbose_name="Дата окончания проекта")  # Поле для валидации даты

    def extend_end_date(self, new_end_date):
        """Метод для продления даты завершения проекта"""
        if new_end_date > self.end_date:
            self.end_date = new_end_date
            self.save()
            return True
        return False

    def save(self, *args, **kwargs):
        if self.end_date and isinstance(self.end_date, datetime):
            self.end_date = self.end_date.date()  # Убедимся, что это дата, если это datetime
        if self.end_date and self.end_date < date.today():  # Проверка на прошедшую дату
            raise ValueError("End date cannot be in the past.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProjectChatMessage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='projects_chat_messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects_chat_messages')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.user} on {self.created_at}"
