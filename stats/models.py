from django.db import models

class UserStatistics(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    completed_tasks = models.IntegerField(default=0)
    completed_projects = models.IntegerField(default=0)
    completed_tickets = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Статистика для {self.user.username} на {self.date}"