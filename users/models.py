from django.contrib.auth.models import User
from django.db import models
from departments.models import Department  # Импортируем модель Department

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('Офис', 'Офис'),
        ('Склад', 'Склад'),
        ('Магазин', 'Магазин'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Офис')  # Добавляем поле role
    job_title = models.CharField(max_length=100, verbose_name="Должность")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Отдел")
    birth_date = models.DateField(null=True, blank=True, verbose_name="День рождения")
    hire_date = models.DateField(null=True, blank=True, verbose_name="Дата устройства в компанию")
    phone_number_mobile = models.CharField(max_length=20, null=True, blank=True, verbose_name="Мобильный телефон")
    phone_number_internal = models.CharField(max_length=10, null=True, blank=True, verbose_name="Внутренний телефон")
    telegram_chat_ID = models.CharField(max_length=50, null=True, blank=True, verbose_name="Telegram ID")
    is_store_account = models.BooleanField(default=False)  # Устанавливаем значение по умолчанию
    full_statistics = models.BooleanField(default=False, verbose_name='Полная статистика')

    # Новые поля для прав
    can_post_news = models.BooleanField(default=False, verbose_name="Разрешить постить новости")
    can_edit_news = models.BooleanField(default=False, verbose_name="Разрешить редактировать новости")

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.job_title})"
