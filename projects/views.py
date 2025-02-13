from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Project
from tasks.models import Task
from chats.models import ProjectChatMessage
from attachments.forms import AttachmentForm
from chats.forms import ProjectChatMessageForm
from .forms import ProjectForm
from notifications.utils import create_notification  # Импортируем функцию уведомлений
from collections import defaultdict
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from departments.models import Department
from participants.models import Participant
from django.contrib import messages
from .forms import ProjectExtendEndDateForm

def project_list(request):
    query = request.GET.get('query', '')
    year = request.GET.get('year', '')
    month = request.GET.get('month', '')
    user = request.user

    # Преобразуем параметры года и месяца в числа, если они переданы
    try:
        year = int(year) if year else None
    except ValueError:
        year = None

    try:
        month = int(month) if month else None
    except ValueError:
        month = None

    # Фильтруем проекты, связанные с пользователем
    projects = Project.objects.filter(
        Q(manager=user) | 
        Q(participants__user=user)
    ).distinct()

    if query:
        projects = projects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    if year:
        projects = projects.filter(created_at__year=year)
    if month:
        projects = projects.filter(created_at__month=month)

    active_projects = projects.exclude(status='completed').order_by('-created_at')
    completed_projects = projects.filter(status='completed').order_by('-created_at')

    # Доступные годы и месяцы
    years = Project.objects.dates('created_at', 'year', order='DESC')
    months = {
        1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель', 5: 'Май', 6: 'Июнь',
        7: 'Июль', 8: 'Август', 9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
    }

        # Добавьте вычисление процента завершения
    for project in active_projects:
        total_tasks = project.tasks.count()
        completed_tasks = project.tasks.filter(status='completed').count()
        project.completion_percentage = (
            (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        )

    return render(request, 'projects/project_list.html', {
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'query': query,
        'years': years,
        'months': months,
        'selected_year': year,
        'selected_month': month,
    })

def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = project.tasks.select_related('assignee').all()
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='completed').count()
    project.completion_percentage = (
        (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
    )
    chat_messages = ProjectChatMessage.objects.filter(project=project)

    department_id = request.GET.get('department')
    departments = Department.objects.all()  # Получаем все отделы из модели Department

    if request.method == 'POST':
        form = ProjectChatMessageForm(request.POST)
        attachment_form = AttachmentForm(request.POST, request.FILES)
        if 'add_message' in request.POST:
            form = ProjectChatMessageForm(request.POST)
            if form.is_valid():
                chat_message = form.save(commit=False)
                chat_message.project = project
                chat_message.user = request.user
                chat_message.save()

                # Отправка уведомления всем участникам проекта
                for participant in project.participants.all():
                    create_notification(participant.user, f'Участник {request.user} добавил сообщение в чате проекта {project.title}', 'email')
                    create_notification(participant.user, f'Участник {request.user} добавил сообщение в чате проекта {project.title}', 'telegram')

                return redirect('project_detail', project_id=project.id)
        elif 'upload_file' in request.POST:
            attachment_form = AttachmentForm(request.POST, request.FILES)
            if attachment_form.is_valid():
                attachment = attachment_form.save(commit=False)
                attachment.project = project
                attachment.uploaded_by = request.user
                attachment.save()

                # Отправка уведомления всем участникам проекта о новом файле
                for participant in project.participants.all():
                    create_notification(participant.user, f'Участник {request.user} добавил файл в проект {project.title}', 'email')
                    create_notification(participant.user, f'Участник {request.user} добавил файл в проект {project.title}', 'telegram')

                return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectChatMessageForm()
        attachment_form = AttachmentForm()

    return render(request, 'projects/project_detail.html', {
        'project': project,
        'tasks': tasks,
        'chat_messages': chat_messages,
        'form': form,
        'attachment_form': attachment_form,
        'departments': departments,
        'current_department': department_id
    })

def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.manager = request.user  # Устанавливаем текущего пользователя как инициатора
            project.status = 'new'  # Устанавливаем статус проекта по умолчанию
            project.save()
            
            return redirect('project_list')
    else:
        form = ProjectForm()
    
    return render(request, 'projects/project_form.html', {'form': form})
    
def project_update(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            print(f"End Date Before Save: {form.cleaned_data.get('end_date')}")  # Отладка
            form.save()
            return redirect('project_detail', project_id=project.id)
        else:
            print(f"Form Errors: {form.errors}")  # Отладка
    else:
        form = ProjectForm(instance=project)
        
        # Преобразование даты окончания в формат для отображения
        if project.end_date:
            form.fields['end_date'].initial = project.end_date.strftime('%Y-%m-%d')
            print(f"Formatted End Date Loaded: {form.fields['end_date'].initial}")  # Отладка
        else:
            print("End Date is not set in the project.")  # Отладка
    
    return render(request, 'projects/project_form.html', {'form': form})

def complete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Проверка всех задач проекта
    incomplete_tasks = project.tasks.filter(status__in=['in_progress', 'pending'])
    if incomplete_tasks.exists():
        messages.error(request, 'Проект не может быть завершен, так как не все задачи завершены.')
        return redirect('project_detail', project_id=project.id)

    project.status = 'completed'
    project.end_date = timezone.now()  # Устанавливаем дату завершения проекта
    project.save()

    # Отправка уведомления участникам проекта
    for participant in project.participants.all():
        create_notification(participant.user, f'Проект "{project.title}" был завершен.', 'email')
        create_notification(participant.user, f'Проект "{project.title}" был завершен.', 'telegram')

    return redirect('project_detail', project_id=project.id)

@login_required
def remove_participant(request, project_id, participant_id):
    project = get_object_or_404(Project, id=project_id)
    participant = get_object_or_404(Participant, id=participant_id)

    # Проверка, что текущий пользователь — инициатор проекта
    if request.user != project.manager:
        return redirect('project_detail', project_id=project.id)

    # Удаление участника
    participant.delete()
    return redirect('project_detail', project_id=project.id)

@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.user == project.manager or request.user.has_perm('projects.delete_project'):
        project.delete()
        return redirect('project_list')  # перенаправление на список проектов
    else:
        # обработка ошибки доступа
        return redirect('project_detail', project_id=project.id)  # перенаправление на детальную страницу проекта

@login_required
def extend_project_end_date(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.user != project.manager:
        messages.error(request, "У вас нет прав для продления даты завершения этого проекта.")
        return redirect('project_detail', project_id=project.id)

    if request.method == 'POST':
        form = ProjectExtendEndDateForm(request.POST, instance=project)
        if form.is_valid():
            project.end_date = form.cleaned_data['end_date']
            project.save()
            messages.success(request, "Дата завершения проекта успешно продлена.")
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectExtendEndDateForm(instance=project)

    return render(request, 'projects/extend_end_date.html', {'form': form, 'project': project})

@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.user != project.manager:
        messages.error(request, "У вас нет прав для редактирования этого проекта.")
        return redirect('project_detail', project_id=project.id)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)  # Используем ProjectForm с объектом
        if form.is_valid():
            form.save()
            messages.success(request, "Проект успешно отредактирован.")
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)  # Загружаем данные проекта для редактирования

    return render(request, 'projects/project_form.html', {'form': form, 'project': project})

def project_tasks_api(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = Task.objects.filter(project=project).values(
        'id', 'title', 'created_at', 'deadline'
    )
    tasks_data = [
        {
            'id': task['id'],
            'name': task['title'],
            'start': task['created_at'].strftime('%Y-%m-%d'),
            'end': task['deadline'].strftime('%Y-%m-%d') if task['deadline'] else None,
            'progress': 50,  # процент выполнения, можно изменить
            'dependencies': ""  # зависимости между задачами, если есть
        }
        for task in tasks
    ]
    return JsonResponse(tasks_data, safe=False)