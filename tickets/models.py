from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date

class Ticket(models.Model):
    STATUS_CHOICES = [
    ('new', 'Новая'),
    ('in_progress', 'В процессе'),
    ('extension_requested', 'Запрос на продление'),
    ('done', 'Выполнена'),
    ('completed', 'Завершена'),
    ('completed_early', 'Завершена досрочно'), 
    ('approval_pending', 'Ожидает согласования'),
    ('in_revision', 'Отправлена на доработку')  # Новый статус
    ]   

    title = models.CharField(max_length=255, verbose_name="Название заявки")
    description = models.TextField(verbose_name="Описание заявки", blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tickets', verbose_name="Автор заявки", null=True, blank=True)
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tickets', verbose_name="Исполнитель", null=True, blank=True)
    observer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='observed_tickets', verbose_name="Наблюдатель")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Статус заявки", default='new')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    accepted_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата принятия")
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата закрытия")
    return_count = models.IntegerField(default=0, verbose_name="Количество возвратов на доработку")
    deadline = models.DateField()
    requested_extension_date = models.DateField(null=True, blank=True)

    def is_overdue(self):
        return self.deadline and self.deadline < date.today()


def save(self, *args, **kwargs):
    # Проверка только при создании объекта (если объект не существует в базе данных)
    if not self.pk and self.deadline and self.deadline < timezone.now().date():
        raise ValueError("Нельзя сохранять объекты с прошедшей датой.")
    
    # Если дедлайн не указан, добавляем 3 дня
    if not self.deadline:
        self.deadline = timezone.now().date() + timedelta(days=3)
    
    super(Ticket, self).save(*args, **kwargs)



class TicketChatMessage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='chat_messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.user} on {self.created_at}"
