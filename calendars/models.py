from django.db import models
from tasks.models import Task
from tickets.models import Ticket
from django.contrib.auth.models import User  # Импорт модели пользователя

class CalendarEvent(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название события")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Связанная задача")
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Связанная заявка")
    start_time = models.DateTimeField(verbose_name="Время начала")
    end_time = models.DateTimeField(verbose_name="Время окончания")
    color = models.CharField(max_length=7, default="#000000", verbose_name="Цвет события")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", related_name="calendar_events")  # Добавляем связь с пользователем

    def __str__(self):
        return self.title
