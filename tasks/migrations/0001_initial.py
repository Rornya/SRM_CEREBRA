# Generated by Django 5.1 on 2024-10-05 14:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Название задачи')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание задачи')),
                ('status', models.CharField(choices=[('new', 'Новый'), ('in_progress', 'В процессе'), ('done', 'Завершенный'), ('approval_pending', 'В процессе одобрения'), ('extension_requested', 'Запрошено продление'), ('completed', 'Завершено')], default='new', max_length=20, verbose_name='Статус задачи')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('accepted_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата принятия')),
                ('closed_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата закрытия')),
                ('return_count', models.IntegerField(default=0, verbose_name='Количество возвратов на доработку')),
                ('revision_count', models.PositiveIntegerField(default=0, verbose_name='Количество исправлений')),
                ('deadline', models.DateField()),
                ('is_approved', models.BooleanField(default=False, verbose_name='Одобрена инициатором')),
                ('assignee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assigned_tasks', to=settings.AUTH_USER_MODEL, verbose_name='Исполнитель')),
                ('assistant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assisting_tasks', to=settings.AUTH_USER_MODEL, verbose_name='Ассистент')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_tasks', to=settings.AUTH_USER_MODEL, verbose_name='Автор задачи')),
                ('observer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='observed_tasks', to=settings.AUTH_USER_MODEL, verbose_name='Наблюдатель')),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='projects.project', verbose_name='Проект')),
            ],
        ),
        migrations.CreateModel(
            name='TaskChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_messages', to='tasks.task')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
