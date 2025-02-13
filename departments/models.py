from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название отдела")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    def __str__(self):
        return self.name
