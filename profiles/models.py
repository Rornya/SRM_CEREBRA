from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile_from_profiles')
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    position = models.CharField(max_length=100, verbose_name="Должность", blank=True)
    department = models.CharField(max_length=100, verbose_name="Отдел", blank=True)
    internal_phone = models.CharField(max_length=20, verbose_name="Телефон внутренний", blank=True)
    mobile_phone = models.CharField(max_length=20, verbose_name="Телефон мобильный", blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True, verbose_name="Фото профиля")
    birthday = models.DateField(verbose_name="Дата рождения", blank=True, null=True)
    hire_date = models.DateField(verbose_name="Дата устройства в компанию", blank=True, null=True)
    email = models.EmailField(verbose_name="Email", blank=True)  # Добавить поле email
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, verbose_name="Фото профиля")  # Добавить поле фото профиля
    date_of_birth = models.DateField(verbose_name="Дата рождения", blank=True, null=True)  # Добавить поле дата рождения
    date_of_joining = models.DateField(verbose_name="Дата устройства", blank=True, null=True)  # Добавить поле дата устройства
    is_store_account = models.BooleanField(default=False, verbose_name="Учетная запись магазина")

    def __str__(self):
        return self.full_name if self.full_name else self.user.username

