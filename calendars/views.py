from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tasks.models import Task
from tickets.models import Ticket
from projects.models import Project
from diary.models import DiaryEntry
from django.db.models import Q
from users.models import UserProfile
from datetime import date
import json
from django.utils.safestring import mark_safe

@login_required
def calendar_view(request):
    user = request.user
    events = {}
    

    # Заявки: отображаем для автора, исполнителя и ассистентов, независимо от статуса
    tickets = Ticket.objects.filter(
        Q(author=user) | Q(assignee=user) | Q(assistants=user),
        deadline__isnull=False
    )
    for ticket in tickets:
        details = f"Автор: {ticket.author.get_full_name()}, Исполнитель: {ticket.assignee.get_full_name() if ticket.assignee else 'Не назначен'}, "
        if ticket.assistants.exists():
            details += f"Ассистенты: {', '.join([a.user.get_full_name() for a in ticket.assistants.all()])}"
        events[ticket.deadline.strftime('%Y-%m-%d')] = {
            'type': 'Заявка',
            'details': details
        }

    # Проектные задачи: отображаем для автора, исполнителя и ассистентов, независимо от статуса
    tasks = Task.objects.filter(
        Q(author=user) | Q(assignee=user) | Q(assistants=user),
        deadline__isnull=False
    )
    for task in tasks:
        details = f"Автор: {task.author.get_full_name()}, Исполнитель: {task.assignee.get_full_name() if task.assignee else 'Не назначен'}, "
        if task.assistants.exists():
            details += f"Ассистенты: {', '.join([a.user.get_full_name() for a in task.assistants.all()])}"
        events[task.deadline.strftime('%Y-%m-%d')] = {
            'type': 'Проектная задача',
            'details': details
        }

    # Окончание проектов
    projects = Project.objects.filter(
        Q(manager=user) | Q(participants__user=user),
        end_date__isnull=False
    )
    for project in projects:
        events[project.end_date.strftime('%Y-%m-%d')] = {
            'type': 'Окончание проекта',
            'details': f"Инициатор: {project.manager.get_full_name()}, Участники: {', '.join([p.user.get_full_name() for p in project.participants.all()])}"
        }

    # Записи из ежедневника
    diary_entries = DiaryEntry.objects.filter(user=user)
    for entry in diary_entries:
        events[entry.entry_date.strftime('%Y-%m-%d')] = {
            'type': 'Запись ежедневника',
            'details': f"Запись: {entry.title}"
        }

    # Дни рождения
    today = date.today()
    birthdays = UserProfile.objects.filter(birth_date__isnull=False)
    for profile in birthdays:
        birthday_date = profile.birth_date.replace(year=today.year).strftime('%Y-%m-%d')
        events[birthday_date] = {
            'type': 'День рождения',
            'details': f"День рождения: {profile.user.get_full_name()}"
        }

    # Передача данных событий в формате JSON
    print(events)  # Вывод данных в консоль для отладки
    return render(request, 'calendars/calendar.html', {
         'events_json': mark_safe(json.dumps(events))  # Передаем данные событий в JSON
    })
