from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import models
from profiles.models import UserProfile  # Импортируем модель UserProfile из приложения profiles

class Activity(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    activity_date = models.DateField()
    activity_time = models.TimeField()
    participants = models.ManyToManyField(UserProfile, related_name="activities")
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('activity_detail', args=[str(self.id)])
