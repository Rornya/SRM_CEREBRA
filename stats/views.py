from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from departments.models import Department
from tasks.models import Task
from tectasks.models import Tectask
from tickets.models import Ticket
from projects.models import Project
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count, Q
from assistants.models import Assistant
from django.db import models

@login_required
def statistics_view(request):
    # Получаем текущего пользователя
    user = request.user

    # Расчет статистики
    # Проекты
    projects_author = Project.objects.filter(manager=user).count()
    projects_participant = Project.objects.filter(participants__user=user).count()

    # Задачи
    tasks_author = Task.objects.filter(author=user).count()
    tasks_executor = Task.objects.filter(assignee=user).count()
    tasks_assistant = Assistant.objects.filter(user=user).count()

    # Заявки
    tickets_author = Ticket.objects.filter(author=user).count()
    tickets_executor = Ticket.objects.filter(assignee=user).count()
    tickets_assistant = Ticket.objects.filter(assistants__user=user).count()


    # Просроченные задачи и заявки
    overdue_tasks = Task.objects.filter(
        assignee=user, deadline__lt=timezone.now(), status='in_progress'
    ).count()
    overdue_tickets = Ticket.objects.filter(
        assignee=user, deadline__lt=timezone.now(), status='in_progress'
    ).count()

    # Возвраты задач и заявок
    reworked_tasks = Task.objects.filter(assignee=user).aggregate(total=models.Sum('return_count'))['total'] or 0
    reworked_tickets = Ticket.objects.filter(assignee=user).aggregate(total=models.Sum('return_count'))['total'] or 0

    # Расчет рейтинга
    user_rating = (
        (tasks_executor + tickets_executor) * 10
        - (overdue_tasks + overdue_tickets) * 5
        - (reworked_tasks + reworked_tickets) * 3
    )

    # Передача данных в шаблон
    return render(request, 'statistics/user_statistics.html', {
        'projects_author': projects_author,
        'projects_participant': projects_participant,
        'tasks_author': tasks_author,
        'tasks_executor': tasks_executor,
        'tasks_assistant': tasks_assistant,
        'tickets_author': tickets_author,
        'tickets_executor': tickets_executor,
        'tickets_assistant': tickets_assistant,
        'overdue_tasks': overdue_tasks,
        'overdue_tickets': overdue_tickets,
        'reworked_tasks': reworked_tasks,
        'reworked_tickets': reworked_tickets,
        'user_rating': user_rating,
    })

@login_required
def employee_load_view(request, employee_id):
    if not request.user.userprofile.full_statistics:
        return render(request, 'statistics/user_statistics.html')
        
    employee = get_object_or_404(User, id=employee_id)
    tasks = Task.objects.filter(assignee=employee)
    tickets = Ticket.objects.filter(assignee=employee)
    projects = Project.objects.filter(manager=employee)

    return render(request, 'statistics/employee_load.html', {
        'employee': employee,
        'tasks': tasks,
        'tickets': tickets,
        'projects': projects
    })

@login_required
def department_statistics(request):
    if not request.user.userprofile.full_statistics:
        return render(request, 'statistics/user_statistics.html')
    
    departments = Department.objects.all().order_by('name')  # Сортируем отделы по имени
    return render(request, 'statistics/departments.html', {'departments': departments})
    
@login_required
def department_employee_statistics(request, department_id):
    # Получаем выбранный отдел
    department = get_object_or_404(Department, id=department_id)

    # Получаем всех пользователей отдела, сортируем по имени
    employees = User.objects.filter(userprofile__department=department).order_by('first_name')

    # Список сотрудников с их статистикой
    employee_statistics = []
    total_rating = 0

    for employee in employees:
        # Проекты: Автор и Участник
        projects_author = Project.objects.filter(manager=employee).count()
        projects_participant = Project.objects.filter(participants__user=employee).count()

        # Заявки: Автор и Исполнитель
        tickets_author = Ticket.objects.filter(author=employee).count()
        tickets_executor = Ticket.objects.filter(assignee=employee).count()

        # Задачи: Автор, Исполнитель и Ассистент
        tasks_author = Task.objects.filter(author=employee).count()
        tasks_executor = Task.objects.filter(assignee=employee).count()
        tasks_assistant = Assistant.objects.filter(task__assignee=employee).count()

        # Заявки, где пользователь ассистент
        tickets_assistant = Assistant.objects.filter(ticket__assignee=employee).count()

        # Просроченные задачи и заявки
        overdue_tasks = Task.objects.filter(
            assignee=employee, deadline__lt=timezone.now(), status='in_progress'
        ).count()
        overdue_tickets = Ticket.objects.filter(
            assignee=employee, deadline__lt=timezone.now(), status='in_progress'
        ).count()

        # Возвраты задач и заявок
        reworked_tasks = Task.objects.filter(assignee=employee).aggregate(total=models.Sum('return_count'))['total'] or 0
        reworked_tickets = Ticket.objects.filter(assignee=employee).aggregate(total=models.Sum('return_count'))['total'] or 0

        # Рассчитываем рейтинг
        rating = (
            (tasks_executor + tickets_executor) * 10  # Вовремя выполнено
            - (overdue_tasks + overdue_tickets) * 5   # Просрочки
            - (reworked_tasks + reworked_tickets) * 3 # Возвраты
        )
        total_rating += max(rating, 0)

        # Собираем статистику по пользователю
        employee_statistics.append({
            'employee': employee.get_full_name(),
            'projects_author': projects_author,
            'projects_participant': projects_participant,
            'tasks_author': tasks_author,
            'tasks_executor': tasks_executor,
            'tasks_assistant': tasks_assistant,
            'tickets_author': tickets_author,
            'tickets_executor': tickets_executor,
            'tickets_assistant': tickets_assistant,
            'overdue_tasks': overdue_tasks,
            'overdue_tickets': overdue_tickets,
            'reworked_tasks': reworked_tasks,
            'reworked_tickets': reworked_tickets,
            'rating': max(rating, 0),
        })

    # Оценка продуктивности отдела
    department_average_rating = total_rating / employees.count() if employees.exists() else 0

    # Передаем данные в шаблон
    return render(request, 'statistics/department_employee_statistics.html', {
        'department': department,
        'employee_statistics': employee_statistics,
        'department_average_rating': round(department_average_rating, 2),
    })

@login_required
def employee_statistics(request, employee_id):
    if not request.user.userprofile.full_statistics:
        return render(request, 'statistics/user_statistics.html')

    employee = get_object_or_404(User, id=employee_id)
    tasks = Task.objects.filter(author=employee) | Task.objects.filter(assignee=employee)
    tickets = Ticket.objects.filter(author=employee) | Ticket.objects.filter(assignee=employee)
    tectasks = Tectask.objects.filter(author=employee) | Tectask.objects.filter(assignee=employee)

    return render(request, 'statistics/employee_statistics.html', {
        'employee': employee,
        'tasks': tasks,
        'tickets': tickets,
        'tectasks': tectasks,
    })
