from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from projects.models import Project
from datetime import date

class Task(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('in_progress', 'В процессе'),
        ('done', 'Завершенный'),
        ('early_completed', 'Завершена досрочно'),
        ('approval_pending', 'В процессе одобрения'),
        ('extension_requested', 'Запрошено продление'),
        ('completed', 'Завершено')
    ]
    title = models.CharField(max_length=255, verbose_name="Название задачи")
    description = models.TextField(verbose_name="Описание задачи", blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', verbose_name="Проект", null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks', verbose_name="Автор задачи", null=True, blank=True)
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks', verbose_name="Исполнитель", null=True, blank=True)
    observer = models.ForeignKey(User, related_name='observed_tasks', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Наблюдатель')
    assistant = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assisting_tasks', verbose_name="Ассистент")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Статус задачи", default='new')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    accepted_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата принятия")
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата закрытия")
    return_count = models.IntegerField(default=0, verbose_name="Количество возвратов на доработку")
    revision_count = models.PositiveIntegerField(default=0, verbose_name="Количество исправлений")
    deadline = models.DateField()
    is_approved = models.BooleanField(default=False, verbose_name="Одобрена инициатором")

    def is_overdue(self):
        return self.deadline and self.deadline < date.today()

    def clean(self):
        # Проверяем, что исполнитель является участником проекта, если проект задан
        if self.project and self.assignee and not self.project.participants.filter(user=self.assignee).exists():
            raise ValidationError(f"Исполнитель {self.assignee} не является участником проекта {self.project.title}")

    def save(self, *args, **kwargs):
        # Проверка, что дата дедлайна не прошла при создании задачи
        if not self.pk and self.deadline and self.deadline < timezone.now().date():
            raise ValidationError("Нельзя сохранять объекты с прошедшей датой.")
        super().save(*args, **kwargs)

    def is_author_project_manager(self):
        """Проверяет, является ли автор задачи инициатором проекта."""
        return self.project and self.project.manager == self.author    

    def __str__(self):
        return self.title

class TaskChatMessage(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='chat_messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.user} on {self.created_at}"
