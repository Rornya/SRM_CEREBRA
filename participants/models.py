from django.db import models
from django.contrib.auth.models import User
from projects.models import Project

class Participant(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, verbose_name="Роль в проекте", default='Участник')

    def __str__(self):
        return f"{self.user} - {self.project}"
