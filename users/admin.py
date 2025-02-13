from django.contrib import admin
from .models import UserProfile
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_title', 'department', 'phone_number_mobile', 'phone_number_internal', 'hire_date')
    list_filter = ('department', 'can_post_news', 'can_edit_news', 'full_statistics')

admin.site.register(UserProfile, UserProfileAdmin)

class CustomUserAdmin(UserAdmin):
    def get_fieldsets(self, request, obj=None):
        """
        Полностью исключаем возможность отображения поля 'is_superuser' для всех, кроме суперпользователей.
        """
        fieldsets = super().get_fieldsets(request, obj)
        if not request.user.is_superuser:
            # Убираем доступ к полю 'is_superuser'
            filtered_fieldsets = []
            for fieldset_name, fieldset_opts in fieldsets:
                fields = list(fieldset_opts.get('fields', []))
                if 'is_superuser' in fields:
                    fields.remove('is_superuser')
                if fields:
                    filtered_fieldsets.append((fieldset_name, {'fields': tuple(fields)}))
            return filtered_fieldsets
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        """
        Делаем поле 'is_superuser' доступным только для чтения для всех, кроме суперпользователей.
        """
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            return readonly_fields + ('is_superuser',)
        return readonly_fields


# Перерегистрируем модель User с кастомным админом
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)