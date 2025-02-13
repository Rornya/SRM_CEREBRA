from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Task, TaskChatMessage
from .forms import TaskChatMessageForm, TaskCreationForm, TaskUpdateForm, AddAssistantForm
from attachments.forms import AttachmentForm
from notifications.utils import create_notification
from projects.models import Project
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Case, When, IntegerField
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth.models import User 
from users.models import UserProfile 
from assistants.models import Assistant
from django.db.models import Case, When, IntegerField
from participants.models import Participant

def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    chat_messages = task.chat_messages.all()

    # Проверка доступа: только инициатор проекта (менеджер) или участник проекта
    is_manager = task.project and task.project.manager == request.user
    is_participant = Participant.objects.filter(project=task.project, user=request.user).exists()

    if not (is_manager or is_participant):
        raise PermissionDenied("У вас нет доступа к этой задаче.")

        # Добавляем информацию об автоматическом одобрении
    auto_approved = task.is_author_project_manager() and task.status == 'in_progress' and not task.is_approved  # Автоматическое одобрение          

    # Форма для чата и формы для загрузки файлов
    form = TaskChatMessageForm()
    attachment_form = AttachmentForm()
    task_link = request.build_absolute_uri(reverse('task_detail', args=[task.id]))
    observer = task.observer

    if request.method == 'POST':
        # Добавление сообщения в чат
        if 'add_message' in request.POST:
            form = TaskChatMessageForm(request.POST)
            if form.is_valid():
                chat_message = form.save(commit=False)
                chat_message.task = task
                chat_message.user = request.user
                chat_message.save()

                # Отправка уведомлений
                recipients = [task.assignee, task.author]
                if task.observer:
                    recipients.append(task.observer)
                for recipient in recipients:
                    create_notification(recipient, f'{request.user} написал сообщение в чате задачи: {task.title}', 'email', link=task_link)
                    create_notification(recipient, f'{request.user} написал сообщение в чате задачи: {task.title}', 'telegram', link=task_link)

                return redirect('task_detail', task_id=task.id)

        # Загрузка файла
        elif 'upload_file' in request.POST:
            attachment_form = AttachmentForm(request.POST, request.FILES)
            if attachment_form.is_valid():
                attachment = attachment_form.save(commit=False)
                attachment.task = task
                attachment.uploaded_by = request.user
                attachment.save()

                # Отправка уведомлений
                recipients = [task.assignee, task.author]
                if task.observer:
                    recipients.append(task.observer)
                for recipient in recipients:
                    create_notification(recipient, f'{request.user} добавил файл в задачу: {task.title}', 'email', link=task_link)
                    create_notification(recipient, f'{request.user} добавил файл в задачу: {task.title}', 'telegram', link=task_link)

                return redirect('task_detail', task_id=task.id)

        # Подтверждение завершения
        elif 'confirm_completion' in request.POST:
            task.status = 'completed'
            task.save()
            create_notification(task.assignee, f'Задача "{task.title}" была подтверждена автором как завершенная.', 'email', link=task_link)
            create_notification(task.assignee, f'Задача "{task.title}" была подтверждена автором как завершенная.', 'telegram', link=task_link)
            return redirect('task_detail', task_id=task.id)

        # Завершение задачи исполнителем
        elif 'complete_task' in request.POST:
            task.status = 'done'
            task.save()
            create_notification(task.author, f'Задача "{task.title}" завершена и ожидает вашего подтверждения.', 'email', link=task_link)
            create_notification(task.author, f'Задача "{task.title}" завершена и ожидает вашего подтверждения.', 'telegram', link=task_link)
            return redirect('task_detail', task_id=task.id)

        # Запрос на продление
        elif 'request_extension_task' in request.POST:
            task.status = 'extension_requested'
            task.save()
            create_notification(task.author, f'Запрошено продление задачи "{task.title}"', 'email', link=task_link)
            create_notification(task.author, f'Запрошено продление задачи "{task.title}"', 'telegram', link=task_link)
            return redirect('task_detail', task_id=task.id)

        # Подтверждение продления
        elif 'approve_extension' in request.POST:
            task.status = 'in_progress'
            task.deadline += timedelta(days=3)
            task.save()
            create_notification(task.assignee, f'Продление задачи "{task.title}" подтверждено, дедлайн продлен на 3 дня.', 'email', link=task_link)
            create_notification(task.assignee, f'Продление задачи "{task.title}" подтверждено, дедлайн продлен на 3 дня.', 'telegram', link=task_link)
            return redirect('task_detail', task_id=task.id)

        # Отказ в продлении
        elif 'deny_extension' in request.POST:
            task.status = 'in_progress'
            task.save()
            create_notification(task.assignee, f'Продление задачи "{task.title}" было отклонено.', 'email', link=task_link)
            create_notification(task.assignee, f'Продление задачи "{task.title}" было отклонено.', 'telegram', link=task_link)
            return redirect('task_detail', task_id=task.id)

        # Возврат задачи на доработку
        elif 'return_for_revision' in request.POST:
            task.status = 'revision'
            task.revision_count += 1
            task.save()
            create_notification(task.assignee, f'Задача "{task.title}" была возвращена на доработку.', 'email', link=task_link)
            create_notification(task.assignee, f'Задача "{task.title}" была возвращена на доработку.', 'telegram', link=task_link)
            return redirect('task_detail', task_id=task.id)

        # Досрочное завершение задачи
        elif 'early_complete_task' in request.POST:
            task.status = 'completed'  # Устанавливаем статус 'completed'
            task.save()
            create_notification(task.assignee, f'Задача "{task.title}" была завершена досрочно автором.', 'email', link=task_link)
            create_notification(task.assignee, f'Задача "{task.title}" была завершена досрочно автором.', 'telegram', link=task_link)
            return redirect('task_detail', task_id=task.id)

    return render(request, 'tasks/task_detail.html', {
        'task': task,
        'form': TaskChatMessageForm(),
        'chat_messages': task.chat_messages.all(),
        'attachment_form': AttachmentForm(),
        'project_id': task.project.id,
        'auto_approved': auto_approved
    })
    
@login_required
def task_create(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        form = TaskCreationForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.author = request.user

            # Если автор задачи является инициатором проекта, задача сразу переходит в статус "В работе"
            if request.user == project.manager:
                task.status = 'in_progress'
            else:
                task.status = 'approval_pending'  # Для остальных участников статус "В процессе одобрения"
            
            task.save()

            # Проверка: исполнитель задачи должен быть участником проекта
            project_users = project.participants.values_list('user', flat=True)
            print(f"Исполнитель: {task.assignee.id}, Участники проекта: {list(project_users)}")  # Отладочная информация
            if task.assignee.id not in project_users:
                raise PermissionDenied("Исполнитель должен быть участником проекта")

            # Логика для добавления наблюдателей
            observer = form.cleaned_data.get('observer')
            if observer:
                task.observer = observer
                task.save()
                
            task_link = request.build_absolute_uri(reverse('task_detail', args=[task.id]))

            # Уведомления
            if request.user != project.manager:
                # Уведомление инициатору проекта, если задача создана другим участником
                initiator = project.manager
                message = f"Участник проекта {project.title} ({request.user.get_full_name()}) создал задачу '{task.title}', которая ждет Вашего одобрения."
                create_notification(initiator, message, 'email', link=task_link)
                create_notification(initiator, message, 'telegram', link=task_link)
            else:
                # Уведомление исполнителю, если задача сразу перешла в работу
                message = f"Задача '{task.title}' была создана и сразу отправлена вам в работу."
                create_notification(task.assignee, message, 'email', link=task_link)
                create_notification(task.assignee, message, 'telegram', link=task_link)

            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskCreationForm(project=project)  # Передаем проект в форму

    observer_users = UserProfile.objects.filter(full_statistics=True).select_related('user')
    return render(request, 'tasks/task_create.html', {
        'form': form,
        'project': project,
        'observer_users': observer_users,
        'project_id': project_id
    })


def task_update(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        form = TaskUpdateForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()

            task_link = request.build_absolute_uri(reverse('task_detail', args=[task.id]))

            # Уведомление об обновлении задачи
            create_notification(task.assignee, f'Задача "{task.title}" была обновлена.', 'email', link=task_link)
            create_notification(task.assignee, f'Задача "{task.title}" была обновлена.', 'telegram', link=task_link)

            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskUpdateForm(instance=task, project=project)  # Передаем проект в форму
    return render(request, 'tasks/task_update.html', {'form': form, 'task': task})

@login_required
def task_list(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Фильтрация задач по пользователю
    project_tasks = Task.objects.filter(
        project_id=project_id
    ).filter(
        Q(author=request.user) | Q(assignee=request.user) | Q(task_assistants__user=request.user)
    ).distinct().order_by(
        Case(
            When(status='completed', then=1),
            When(status='early_completed', then=1),  # Досрочно завершённые внизу
            default=0,
            output_field=IntegerField(),
        ),
        'created_at'
    )

    tasks_with_status = []
    for task in project_tasks:
        task.is_assistant = task.task_assistants.filter(user=request.user).exists()
        task.is_observer = task.observer == request.user
        tasks_with_status.append(task)

    return render(request, 'tasks/task_list.html', {
        'tasks': tasks_with_status,
        'project': project
    })

def task_return_for_revision(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.status = 'revision'
        task.revision_count += 1
        task.save()
        task_link = request.build_absolute_uri(reverse('task_detail', args=[task.id]))

        # Уведомление о возврате задачи
        create_notification(task.assignee, f'Задача "{task.title}" была возвращена на доработку.', 'email', link=task_link)
        create_notification(task.assignee, f'Задача "{task.title}" была возвращена на доработку.', 'telegram', link=task_link)

        return redirect('task_detail', task_id=task.id)

    return redirect('task_detail', task_id=task.id)

def accept_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.status = 'in_progress'
    task.save()

    task_link = request.build_absolute_uri(reverse('task_detail', args=[task.id]))

    # Уведомление о принятии задачи
    create_notification(task.assignee, f'Вы приняли задачу "{task.title}".', 'email', link=task_link)
    create_notification(task.assignee, f'Вы приняли задачу "{task.title}".', 'telegram', link=task_link)

    return redirect('task_detail', task_id=task.id)

def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    # Изменяем статус задачи на "выполнено"
    if request.method == 'POST':
        task.status = 'done'
        task.save()

        task_link = request.build_absolute_uri(reverse('task_detail', args=[task.id]))

        # Уведомление автору задачи о том, что задача выполнена и ожидает подтверждения
        create_notification(task.author, f'Задача "{task.title}" в проекте "{task.project.title}" была завершена и ожидает вашего подтверждения.', 'email', link=task_link)
        create_notification(task.author, f'Задача "{task.title}" в проекте "{task.project.title}" была завершена и ожидает вашего подтверждения.', 'telegram', link=task_link)

        return redirect('task_detail', task_id=task.id)

    return redirect('task_detail', task_id=task.id)
    
def request_extension_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.status = 'extension_requested'
    task.save()

    task_link = request.build_absolute_uri(reverse('task_detail', args=[task.id]))

    # Уведомление о запросе продления задачи
    create_notification(task.author, f'Запрошено продление задачи "{task.title}".', 'email', link=task_link)
    create_notification(task.author, f'Запрошено продление задачи "{task.title}".', 'telegram', link=task_link)

    return redirect('task_detail', task_id=task.id)

@login_required
def approve_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user == task.project.manager:  # Только инициатор может одобрить задачу
        task.status = 'in_progress'  # Изменяем статус на 'in_progress'
        task.save()

        task_link = request.build_absolute_uri(reverse('task_detail', args=[task.id]))

        # Уведомляем исполнителя о том, что задача одобрена
        create_notification(task.assignee, f'Задача "{task.title}" одобрена и переведена в статус "В работе".', 'email', link=task_link)
        create_notification(task.assignee, f'Задача "{task.title}" одобрена и переведена в статус "В работе".', 'telegram', link=task_link)
        messages.success(request, f"Задача '{task.title}' была одобрена и отправлена исполнителю.")
    
    return redirect('project_detail', project_id=task.project.id)

@login_required
def reject_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user == task.project.manager:  # Только инициатор может отклонить задачу
        task.status = 'rejected'  # Изменяем статус на 'rejected'
        task.save()

        task_link = request.build_absolute_uri(reverse('task_detail', args=[task.id]))

        # Уведомляем автора задачи о том, что задача отклонена
        create_notification(task.author, f'Задача "{task.title}" отклонена инициатором проекта.', 'email', link=task_link)
        create_notification(task.author, f'Задача "{task.title}" отклонена инициатором проекта.', 'telegram', link=task_link)
        messages.error(request, f"Задача '{task.title}' была отклонена.")
    
    return redirect('project_detail', project_id=task.project.id)

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user == task.author or request.user.has_perm('tasks.delete_task'):
        task.delete()
        return redirect('task_list', project_id=task.project.id)  # перенаправление на список задач проекта
    else:
        # обработка ошибки доступа
        return redirect('task_detail', task_id=task.id)

@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    project = task.project

    if request.method == 'POST':
        form = TaskUpdateForm(request.POST, instance=task, project=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Задача успешно отредактирована.")
            return redirect('task_list', project_id=project.id)
    else:
        form = TaskUpdateForm(instance=task, project=project)

    return render(request, 'tasks/task_edit.html', {
        'form': form,
        'task': task,
        'project': project,
        'project_id': project.id
    })

