from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('email', 'Email'),
        ('telegram', 'Telegram'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Получатель")
    message = models.TextField(verbose_name="Сообщение")
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, verbose_name="Тип уведомления")
    link = models.URLField(blank=True, null=True, verbose_name="Ссылка на объект")  
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_sent = models.BooleanField(default=False, verbose_name="Отправлено")

    def __str__(self):
        return f"Уведомление для {self.user.username} - {self.notification_type}"
