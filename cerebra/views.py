from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from news.models import NewsPost
from calendars.models import CalendarEvent  
from django.contrib.auth.decorators import login_required
from tasks.models import Task
from tickets.models import Ticket
from projects.models import Project  
from diary.models import DiaryEntry
from tectasks.models import Tectask  
from django.db.models import Q 
from django.contrib.auth.models import User
from datetime import datetime 
from datetime import date
from users.models import UserProfile
from birthdays.views import birthdays_list
from participants.models import Participant
from activities.models import Activity
from django.http import JsonResponse
from django.utils.safestring import mark_safe
import json
from django.core.serializers.json import DjangoJSONEncoder

@login_required
def home(request):
    # Получаем текущего пользователя и его роль
    user = request.user
    user_role = user.userprofile.role

    # Фильтруем новости на основе роли пользователя
    if user_role == 'Офис':
        news_list = NewsPost.objects.filter(is_published=True, is_visible_for_office=True).order_by('-created_at')[:5]
    elif user_role == 'Склад':
        news_list = NewsPost.objects.filter(is_published=True, is_visible_for_warehouse=True).order_by('-created_at')[:5]
    elif user_role == 'Магазин':
        news_list = NewsPost.objects.filter(is_published=True, is_visible_for_store=True).order_by('-created_at')[:5]
    else:
        news_list = NewsPost.objects.none()

    # Фильтруем только незавершенные задачи, где пользователь является исполнителем, автором или ассистентом
    tasks = Task.objects.filter(
        Q(assignee=user) | Q(author=user) | Q(assistant=user)
    ).exclude(status__in=['completed', 'early_completed']).distinct()
    
    # Фильтруем только незавершенные заявки, где пользователь является исполнителем, автором или ассистентом
    tickets = Ticket.objects.filter(
        Q(assignee=user) | Q(author=user) | Q(assistants__user=user)
    ).exclude(status__in=['completed', 'completed_early']).distinct()

    # Фильтруем только незавершенные текущие задачи (Tectask), где пользователь - автор, исполнитель, наблюдатель или ассистент
    tectasks = Tectask.objects.filter(
        Q(author=user) | Q(assignee=user) | Q(observer=user) | Q(assistants=user)
    ).exclude(status='completed').distinct()

    # Фильтруем только незавершенные проекты
    projects = Project.objects.filter(
        (Q(manager=user) | Q(participants__user=user)) & Q(status__in=['new', 'in_progress'])
    ).distinct()

    # Фильтруем записи из ежедневника, созданные текущим пользователем
    diary_entries = DiaryEntry.objects.filter(user=user)

    # Фильтруем мероприятия, которые еще не завершились
    activities = Activity.objects.filter(activity_date__gte=date.today()).order_by('activity_date')[:5]

    # Загрузка дней рождения для календаря
    today = date.today()
    birthdays = UserProfile.objects.filter(birth_date__isnull=False)
    birthday_events = []
    for profile in birthdays:
        if profile.birth_date:
            birthday_date = profile.birth_date.replace(year=today.year)
            birthday_events.append({
                'title': f"День рождения: {profile.user.get_full_name()}",
                'start': birthday_date.strftime('%Y-%m-%d'),
                'allDay': True,
                'color': '#ffcc00',  # Цвет для дней рождения
            })

    # Задаем флаг для отображения календаря
    show_calendar = True

    # Отображаем задачи, которые требуют одобрения (только для менеджеров проектов)
    tasks_approval_pending = Task.objects.filter(project__manager=user, status='approval_pending')

    return render(request, 'home.html', {
        'news_list': news_list,
        'tasks': tasks,
        'tickets': tickets,
        'tectasks': tectasks,
        'diary_entries': diary_entries,
        'tasks_approval_pending': tasks_approval_pending,
        'birthday_events': birthday_events,
        'projects': projects,
        'show_calendar': show_calendar  # Флаг всегда True
    })

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

def contacts_view(request):
    return render(request, 'contacts.html')

@login_required
def day_view(request, date):
    try:
        selected_date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        selected_date = None

    if selected_date:
        # Фильтруем только незавершенные задачи, заявки и текущие задачи
        tasks = Task.objects.filter(
            deadline=selected_date,
            status__in=['new', 'in_progress']  # Указываем активные статусы
        ).filter(
            Q(assignee=request.user) | Q(author=request.user) | Q(assistant=request.user)
        )
        
        tickets = Ticket.objects.filter(
            deadline=selected_date
        ).exclude(
            status__in=['completed', 'completed_early']
        ).filter(
            Q(assignee=request.user) | Q(author=request.user) | Q(assistants__user=request.user)
        )

        tectasks = Tectask.objects.filter(
            deadline=selected_date
        ).exclude(
            status__in=['completed', 'early_completed']
        ).filter(
            Q(assignee=request.user) | Q(author=request.user) | Q(observer=request.user) | Q(assistants=request.user)
        )

        diary_entries = DiaryEntry.objects.filter(entry_date=selected_date, user=request.user)

        # Фильтруем мероприятия на выбранную дату
        activities = Activity.objects.filter(activity_date=selected_date)


        # Фильтруем только незавершенные проекты, у которых дата окончания - выбранная дата
        projects = Project.objects.filter(
            end_date=selected_date,
            status__in=['new', 'in_progress']
        ).filter(
            Q(manager=request.user) | Q(participants__user=request.user)
        ).distinct()

        return render(request, 'day_view.html', {
            'selected_date': selected_date,
            'tasks': tasks,
            'tickets': tickets,
            'tectasks': tectasks,
            'diary_entries': diary_entries,
            'projects': projects,
            'activities': activities,
        })
    else:
        return render(request, 'day_view.html', {'error': 'Неверный формат даты'})

@login_required
@xframe_options_exempt
def gantt_view(request):
    user = request.user
    gantt_data = []

    # 1. Проекты (основная группировка) - Исключаем завершённые
    projects = Project.objects.filter(
        Q(manager=user) | Q(participants__user=user),
        end_date__isnull=False
    ).exclude(status='completed').distinct()
    project_ids = {}

    for project in projects:
        project_id = f'project-{project.id}'
        project_ids[project.id] = project_id
        gantt_data.append({
            'id': project_id,
            'name': f"Проект: {project.title}",
            'start': project.created_at.strftime('%Y-%m-%d'),
            'end': project.end_date.strftime('%Y-%m-%d'),
            'progress': 100,
            'custom_class': 'project-bar'
        })

    # 2. Задачи, привязанные к проектам - Исключаем завершённые
    tasks = Task.objects.filter(
        Q(author=user) | Q(assignee=user) | Q(task_assistants__user=user),
        deadline__isnull=False
    ).exclude(status='completed').distinct()
    for task in tasks:
        project_dependency = project_ids.get(task.project.id) if task.project else None
        gantt_data.append({
            'id': f'task-{task.id}',
            'name': f"Задача: {task.title}",
            'start': task.created_at.strftime('%Y-%m-%d'),
            'end': task.deadline.strftime('%Y-%m-%d'),
            'progress': 50,
            'dependencies': project_dependency,
            'custom_class': 'bar-blue'
        })

    # 3. Заявки - Исключаем завершённые
    tickets = Ticket.objects.filter(
        Q(author=user) | Q(assignee=user) | Q(assistants__user=user),
        deadline__isnull=False
    ).exclude(status='completed').distinct()
    for ticket in tickets:
        gantt_data.append({
            'id': f'ticket-{ticket.id}',
            'name': f"Заявка: {ticket.title}",
            'start': ticket.created_at.strftime('%Y-%m-%d'),
            'end': ticket.deadline.strftime('%Y-%m-%d'),
            'progress': 0,
            'custom_class': 'bar-green'
        })

    # 4. Мероприятия - оставляем всё
    activities = Activity.objects.filter(activity_date__gte=date.today()).distinct()
    for activity in activities:
        gantt_data.append({
            'id': f'activity-{activity.id}',
            'name': f"Мероприятие: {activity.title}",
            'start': activity.activity_date.strftime('%Y-%m-%d'),
            'end': activity.activity_date.strftime('%Y-%m-%d'),
            'progress': 0,
            'custom_class': 'bar-purple'
        })

    # 5. Записи из ежедневника - оставляем всё
    diary_entries = DiaryEntry.objects.filter(user=user).distinct()
    for entry in diary_entries:
        gantt_data.append({
            'id': f'diary-{entry.id}',
            'name': f"Запись: {entry.title}",
            'start': entry.entry_date.strftime('%Y-%m-%d'),
            'end': entry.entry_date.strftime('%Y-%m-%d'),
            'progress': 0,
            'custom_class': 'bar-orange'
        })

    return render(request, 'gantt.html', {
        'gantt_data': mark_safe(json.dumps(gantt_data))
    })

@login_required
@xframe_options_exempt
def gantt_fullscreen_view(request):
    user = request.user
    gantt_data = []

    # 1. Проекты - Исключаем завершённые
    projects = Project.objects.filter(
        Q(manager=user) | Q(participants__user=user),
        end_date__isnull=False
    ).exclude(status='completed').distinct()
    project_ids = {}

    for project in projects:
        project_id = f'project-{project.id}'
        project_ids[project.id] = project_id
        gantt_data.append({
            'id': project_id,
            'name': f"Проект: {project.title}",
            'start': project.created_at.strftime('%Y-%m-%d'),
            'end': project.end_date.strftime('%Y-%m-%d'),
            'progress': 100,
            'custom_class': 'project-bar',
            'link': f"/projects/projects/{project.id}/"
        })

    # 2. Задачи - Исключаем завершённые
    tasks = Task.objects.filter(
        Q(author=user) | Q(assignee=user) | Q(task_assistants__user=user),
        deadline__isnull=False
    ).exclude(status='completed').distinct()
    for task in tasks:
        project_dependency = project_ids.get(task.project.id) if task.project else None
        gantt_data.append({
            'id': f'task-{task.id}',
            'name': f"Задача: {task.title}",
            'start': task.created_at.strftime('%Y-%m-%d'),
            'end': task.deadline.strftime('%Y-%m-%d'),
            'progress': 50,
            'dependencies': project_dependency,
            'custom_class': 'bar-blue',
            'link': f"/tasks/task/{task.id}/"
        })

    # 3. Заявки - Исключаем завершённые
    tickets = Ticket.objects.filter(
        Q(author=user) | Q(assignee=user) | Q(assistants__user=user),
        deadline__isnull=False
    ).exclude(status='completed').distinct()
    for ticket in tickets:
        gantt_data.append({
            'id': f'ticket-{ticket.id}',
            'name': f"Заявка: {ticket.title}",
            'start': ticket.created_at.strftime('%Y-%m-%d'),
            'end': ticket.deadline.strftime('%Y-%m-%d'),
            'progress': 0,
            'custom_class': 'bar-green',
            'link': f"/tickets/{ticket.id}/"  # Ссылка на заявку
        })

    # 4. Мероприятия - оставляем всё
    activities = Activity.objects.filter(activity_date__gte=date.today()).distinct()
    for activity in activities:
        gantt_data.append({
            'id': f'activity-{activity.id}',
            'name': f"Мероприятие: {activity.title}",
            'start': activity.activity_date.strftime('%Y-%m-%d'),
            'end': activity.activity_date.strftime('%Y-%m-%d'),
            'progress': 0,
            'custom_class': 'bar-purple',
            'link': f"/activities/{activity.id}/"  # Ссылка на мероприятие
        })

    # 5. Ежедневник - оставляем всё
    diary_entries = DiaryEntry.objects.filter(user=user).distinct()
    for entry in diary_entries:
        gantt_data.append({
            'id': f'diary-{entry.id}',
            'name': f"Запись: {entry.title}",
            'start': entry.entry_date.strftime('%Y-%m-%d'),
            'end': entry.entry_date.strftime('%Y-%m-%d'),
            'progress': 0,
            'custom_class': 'bar-orange',
            'link': f"/diary/{entry.id}/"  # Ссылка на запись
        })

    return render(request, 'gantt_fullscreen.html', {
        'gantt_data': mark_safe(json.dumps(gantt_data))
    })

