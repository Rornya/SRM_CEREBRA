from django.db import models
from django.contrib.auth.models import User
from tickets.models import Ticket
from tectasks.models import Tectask  # Импортируем модель Tectask
from tasks.models import Task  # Импортируем модель Task

class Assistant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, related_name='task_assistants', on_delete=models.CASCADE, null=True, blank=True)
    ticket = models.ForeignKey(Ticket, related_name="assistants", on_delete=models.CASCADE, null=True, blank=True)  # Поле для Ticket
    tectask = models.ForeignKey(Tectask, related_name="assigned_assistants", on_delete=models.CASCADE, null=True, blank=True)  # Поле для Tectask с уникальным related_name

    def __str__(self):
        return f"{self.user.get_full_name()} - Ассистент"
