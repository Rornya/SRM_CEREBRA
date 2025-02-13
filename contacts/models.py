from django.db import models
from django.contrib.auth.models import User

class Contact(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    position = models.CharField(max_length=100, verbose_name="Должность", blank=True)
    department = models.CharField(max_length=100, verbose_name="Отдел", blank=True)
    internal_phone = models.CharField(max_length=10, verbose_name="Внутренний телефон", blank=True)
    mobile_phone = models.CharField(max_length=15, verbose_name="Мобильный телефон", blank=True)
    email = models.EmailField(verbose_name="Email")

    def __str__(self):
        return self.full_name
