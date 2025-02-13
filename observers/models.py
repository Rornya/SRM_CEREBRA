from django.db import models
from django.contrib.auth.models import User
from tickets.models import Ticket
from tasks.models import Task
from tectasks.models import Tectask
from projects.models import Project

class Observer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Наблюдатель")
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True, blank=True, related_name='ticket_observers')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='task_observers')
    tectask = models.ForeignKey(Tectask, on_delete=models.CASCADE, null=True, blank=True, related_name='tectask_observers')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='project_observers')
    
    class Meta:
        verbose_name = "Наблюдатель"
        verbose_name_plural = "Наблюдатели"

    def __str__(self):
        return f"{self.user.get_full_name()} (Наблюдатель)"
