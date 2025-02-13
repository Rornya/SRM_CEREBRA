from django.db import models
from django.contrib.auth.models import User

class DiaryEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    entry_date = models.DateField(verbose_name="Дата записи")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Запись в ежедневнике"
        verbose_name_plural = "Записи в ежедневнике"
        ordering = ['-entry_date']

    def __str__(self):
        return f"{self.title} - {self.entry_date}"
