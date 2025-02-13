from django.db import models
from django.contrib.auth.models import User
from tasks.models import Task
from tickets.models import Ticket
from tectasks.models import Tectask
from projects.models import Project

class Attachment(models.Model):
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Загружено пользователем")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='attachments', verbose_name="Задача")
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True, blank=True, related_name='attachments', verbose_name="Заявка")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='attachments', verbose_name="Проект")
    tectask = models.ForeignKey(Tectask, on_delete=models.CASCADE, null=True, blank=True, related_name='attachments', verbose_name="Текущая задача")
    def __str__(self):
        return f"Файл: {self.file.name}, Проект: {self.project}, Задача: {self.task}, Текущая Задача: {self.tectask},Заявка: {self.ticket}"

