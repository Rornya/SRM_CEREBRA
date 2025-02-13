from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Tectask, TectaskChatMessage
from .forms import TectaskChatMessageForm, TectaskCreationForm, AddAssistantForm, TectaskUpdateForm
from attachments.forms import AttachmentForm
from notifications.utils import create_notification
from django.http import JsonResponse 
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q  
from django.contrib import messages
from users.models import UserProfile
from departments.models import Department
from assistants.models import Assistant

def tectask_detail(request, tectask_id):
    tectask = get_object_or_404(Tectask, id=tectask_id)
    chat_messages = tectask.chat_messages.all()

    form = TectaskChatMessageForm()
    attachment_form = AttachmentForm()
    assistant_form = AddAssistantForm()
    assistants = Assistant.objects.filter(tectask=tectask)

    tectask_link = request.build_absolute_uri(reverse('tectask_detail', args=[tectask.id]))

    if request.method == 'POST':
        if 'add_message' in request.POST:
            form = TectaskChatMessageForm(request.POST)
            if form.is_valid():
                chat_message = form.save(commit=False)
                chat_message.tectask = tectask
                chat_message.user = request.user
                chat_message.save()

                recipients = [tectask.assignee, tectask.author]
                if tectask.observer:
                    recipients.append(tectask.observer)
                for assistant in assistants:
                    recipients.append(assistant.user)

                for recipient in recipients:
                    create_notification(recipient, f'{request.user} написал сообщение в чате задачи: {tectask.title}', 'email', link=tectask_link)
                    create_notification(recipient, f'{request.user} написал сообщение в чате задачи: {tectask.title}', 'telegram', link=tectask_link)

                return redirect('tectask_detail', tectask_id=tectask.id)

        elif 'upload_file' in request.POST:
            attachment_form = AttachmentForm(request.POST, request.FILES)
            if attachment_form.is_valid():
                attachment = attachment_form.save(commit=False)
                attachment.tectask = tectask
                attachment.uploaded_by = request.user
                attachment.save()

                recipients = [tectask.assignee, tectask.author]
                if tectask.observer:
                    recipients.append(tectask.observer)
                for assistant in assistants:
                    recipients.append(assistant.user)

                for recipient in recipients:
                    create_notification(recipient, f'{request.user} добавил файл к задаче: {tectask.title}', 'email', link=tectask_link)
                    create_notification(recipient, f'{request.user} добавил файл к задаче: {tectask.title}', 'telegram', link=tectask_link)

                return redirect('tectask_detail', tectask_id=tectask.id)

        elif 'accept_tectask' in request.POST:
            tectask.status = 'in_progress'
            tectask.accepted_at = timezone.now()
            tectask.save()

            create_notification(tectask.author, f'Исполнитель принял задачу: {tectask.title}', 'email', link=tectask_link)
            create_notification(tectask.author, f'Исполнитель принял задачу: {tectask.title}', 'telegram', link=tectask_link)

            return redirect('tectask_detail', tectask_id=tectask.id)

        elif 'complete_tectask' in request.POST:
            tectask.status = 'done'
            tectask.save()

            create_notification(tectask.author, f'Исполнитель завершил задачу: {tectask.title}', 'email', link=tectask_link)
            create_notification(tectask.author, f'Исполнитель завершил задачу: {tectask.title}', 'telegram', link=tectask_link)

            return redirect('tectask_detail', tectask_id=tectask.id)

        elif 'request_extension' in request.POST:
            tectask.status = 'extension_requested'
            tectask.save()

            create_notification(tectask.author, f'Запрошено продление задачи: {tectask.title}', 'email', link=tectask_link)
            create_notification(tectask.author, f'Запрошено продление задачи: {tectask.title}', 'telegram', link=tectask_link)

            return redirect('tectask_detail', tectask_id=tectask.id)

        elif 'confirm_completion' in request.POST:
            tectask.status = 'completed'
            tectask.closed_at = timezone.now()
            tectask.save()

            create_notification(tectask.assignee, f'Автор подтвердил завершение задачи: {tectask.title}', 'email', link=tectask_link)
            create_notification(tectask.assignee, f'Автор подтвердил завершение задачи: {tectask.title}', 'telegram', link=tectask_link)

            return redirect('tectask_detail', tectask_id=tectask.id)

        elif 'approve_extension' in request.POST:
            tectask.status = 'in_progress'
            tectask.deadline = tectask.deadline + timedelta(days=3)
            tectask.save()

            create_notification(tectask.assignee, f'Автор подтвердил продление задачи: {tectask.title}, дедлайн продлен на 3 дня', 'email', link=tectask_link)
            create_notification(tectask.assignee, f'Автор подтвердил продление задачи: {tectask.title}, дедлайн продлен на 3 дня', 'telegram', link=tectask_link)

            return redirect('tectask_detail', tectask_id=tectask.id)

        elif 'deny_extension' in request.POST:
            tectask.status = 'in_progress'
            tectask.save()

            create_notification(tectask.assignee, f'Запрос на продление задачи: {tectask.title} был отклонен автором.', 'email', link=tectask_link)
            create_notification(tectask.assignee, f'Запрос на продление задачи: {tectask.title} был отклонен автором.', 'telegram', link=tectask_link)

            return redirect('tectask_detail', tectask_id=tectask.id)

        elif 'return_for_revision' in request.POST:
            tectask.status = 'in_revision'
            tectask.return_count += 1
            tectask.save()

            recipients = [tectask.assignee]
            if tectask.observer:
                recipients.append(tectask.observer)
            for assistant in assistants:
                recipients.append(assistant.user)

            for recipient in recipients:
                create_notification(recipient, f'Задача "{tectask.title}" была возвращена на доработку автором.', 'email', link=tectask_link)
                create_notification(recipient, f'Задача "{tectask.title}" была возвращена на доработку автором.', 'telegram', link=tectask_link)

            return redirect('tectask_detail', tectask_id=tectask.id)

        elif 'add_assistant' in request.POST:
            assistant_form = AddAssistantForm(request.POST)
            if assistant_form.is_valid():
                assistant_user = assistant_form.cleaned_data['user']
                Assistant.objects.create(tectask=tectask, user=assistant_user)

                create_notification(assistant_user, f'Вы были добавлены в задачу: {tectask.title}', 'email', link=tectask_link)
                create_notification(assistant_user, f'Вы были добавлены в задачу: {tectask.title}', 'telegram', link=tectask_link)

                return redirect('tectask_detail', tectask_id=tectask.id)

    return render(request, 'tectasks/tectask_detail.html', {
        'tectask': tectask,
        'form': form,
        'attachment_form': attachment_form,
        'assistant_form': assistant_form,
        'chat_messages': chat_messages,
        'assistants': assistants,
    })

def tectask_create(request):
    # Фильтрация исполнителей по отделу
    if request.GET.get('department_id'):
        department_id = request.GET.get('department_id')
        assignees = UserProfile.objects.filter(department_id=department_id)
        data = [{'id': user.id, 'full_name': user.user.get_full_name()} for user in assignees]
        return JsonResponse({'assignees': data})

    if request.method == 'POST':
        form = TectaskCreationForm(request.POST)
        if form.is_valid():
            tectask = form.save(commit=False)
            tectask.author = request.user

            # Устанавливаем дедлайн по умолчанию, если не указан
            if not tectask.deadline:
                tectask.deadline = timezone.now() + timedelta(days=3)

            tectask.save()

            # Устанавливаем наблюдателей, если они выбраны
            observers = form.cleaned_data.get('observers')
            if observers:
                tectask.observers.set(observers)

            # Ссылки на детальное отображение текущей задачи
            tectask_link = request.build_absolute_uri(reverse('tectask_detail', args=[tectask.id]))

            # Уведомления для исполнителя и автора
            create_notification(tectask.assignee, f'Вам назначена новая текущая задача: {tectask.title}', 'email', link=tectask_link)
            create_notification(tectask.assignee, f'Вам назначена новая текущая задача: {tectask.title}', 'telegram', link=tectask_link)
            create_notification(tectask.author, f'Вы создали текущую задачу: {tectask.title}', 'email', link=tectask_link)
            create_notification(tectask.author, f'Вы создали текущую задачу: {tectask.title}', 'telegram', link=tectask_link)

            # Уведомления для наблюдателей, если добавлены
            if observers:
                for observer in observers:
                    create_notification(observer.user, f'Вы наблюдатель задачи: {tectask.title}', 'email', link=tectask_link)
                    create_notification(observer.user, f'Вы наблюдатель задачи: {tectask.title}', 'telegram', link=tectask_link)

            return redirect('tectask_detail', tectask_id=tectask.id)
    else:
        form = TectaskCreationForm()

    # Получаем список отделов и учетных записей с полными правами статистики
    observer_users = UserProfile.objects.filter(full_statistics=True)
    departments = Department.objects.all()

    return render(request, 'tectasks/tectask_create.html', {
        'form': form,
        'departments': departments,
        'observer_users': observer_users,
    })

def tectask_update(request, tectask_id):
    tectask = get_object_or_404(Tectask, id=tectask_id)
    if request.method == 'POST':
        form = TectaskUpdateForm(request.POST, instance=tectask)
        if form.is_valid():
            tectask = form.save()

            tectask_link = request.build_absolute_uri(reverse('tectask_detail', args=[tectask.id]))

            # Уведомления для всех участников задачи
            create_notification(tectask.assignee, f'Задача "{tectask.title}" была обновлена.', 'email', link=tectask_link)
            create_notification(tectask.assignee, f'Задача "{tectask.title}" была обновлена.', 'telegram', link=tectask_link)
            create_notification(tectask.author, f'Задача "{tectask.title}" была обновлена.', 'email', link=tectask_link)
            create_notification(tectask.author, f'Задача "{tectask.title}" была обновлена.', 'telegram', link=tectask_link)

            if tectask.observer:
                create_notification(tectask.observer, f'Задача "{tectask.title}" была обновлена.', 'email', link=tectask_link)
                create_notification(tectask.observer, f'Задача "{tectask.title}" была обновлена.', 'telegram', link=tectask_link)

            if tectask.assistants.exists():
                for assistant in tectask.assistants.all():
                    create_notification(assistant, f'Задача "{tectask.title}" была обновлена.', 'email', link=tectask_link)
                    create_notification(assistant, f'Задача "{tectask.title}" была обновлена.', 'telegram', link=tectask_link)

            return redirect('tectask_detail', tectask_id=tectask.id)
    else:
        form = TectaskUpdateForm(instance=tectask)
    return render(request, 'tectasks/tectask_update.html', {'form': form, 'tectask': tectask})

def tectask_list(request):
    user = request.user
    # Фильтруем задачи, связанные с текущим пользователем (исполнитель, автор, наблюдатель или ассистент)
    tectasks = Tectask.objects.filter(
        Q(assignee=user) | 
        Q(author=user) | 
        Q(observer=user) | 
        Q(assistants=user)  # Проверяем, является ли пользователь ассистентом
    ).distinct()
    return render(request, 'tectasks/tectask_list.html', {'tectasks': tectasks})

@login_required
def tectask_return_for_revision(request, tectask_id):
    tectask = get_object_or_404(Tectask, id=tectask_id)

    if request.method == 'POST':
        # Устанавливаем статус задачи как "На доработку"
        tectask.status = 'in_revision'
        tectask.return_count += 1  # Увеличиваем счетчик возвратов
        tectask.save()
        tectask_link = request.build_absolute_uri(reverse('tectask_detail', args=[tectask.id]))

        # Уведомление для исполнителя и участников о возврате задачи на доработку
        recipients = [tectask.assignee]
        if tectask.observer:
            recipients.append(tectask.observer)

        # Добавляем всех ассистентов в список уведомляемых
        for assistant in tectask.assistants.all():
            recipients.append(assistant.user)

            

        # Создаем уведомления для всех участников
        for recipient in recipients:
            create_notification(
                recipient, 
                f'Задача "{tectask.title}" была возвращена на доработку автором.', 
                'email', link=tectask_link
            )
            create_notification(
                recipient, 
                f'Задача "{tectask.title}" была возвращена на доработку автором.', 
                'telegram', link=tectask_link
            )

        return redirect('tectask_detail', tectask_id=tectask.id)

    return redirect('tectask_detail', tectask_id=tectask.id)

def accept_tectask(request, tectask_id):
    tectask = get_object_or_404(Tectask, id=tectask_id)
    tectask.status = 'in_progress'
    tectask.save()
    tectask_link = request.build_absolute_uri(reverse('tectask_detail', args=[tectask.id]))

    # Уведомление о принятии задачи
    create_notification(tectask.assignee, f'Вы приняли задачу "{tectask.title}"', 'email', link=tectask_link)
    create_notification(tectask.assignee, f'Вы приняли задачу "{tectask.title}"', 'telegram', link=tectask_link)

    return redirect('tectask_detail', tectask_id=tectask.id)

def complete_tectask(request, tectask_id):
    tectask = get_object_or_404(Tectask, id=tectask_id)
    tectask.status = 'done'
    tectask.save()
    tectask_link = request.build_absolute_uri(reverse('tectask_detail', args=[tectask.id]))

    # Уведомление автору о завершении задачи
    create_notification(tectask.author, f'Задача "{tectask.title}" завершена и ожидает вашего подтверждения.', 'email', link=tectask_link)
    create_notification(tectask.author, f'Задача "{tectask.title}" завершена и ожидает вашего подтверждения.', 'telegram', link=tectask_link)

    return redirect('tectask_detail', tectask_id=tectask.id)

def request_extension_tectask(request, tectask_id):
    tectask = get_object_or_404(Tectask, id=tectask_id)
    tectask.status = 'extension_requested'
    tectask.save()
    tectask_link = request.build_absolute_uri(reverse('tectask_detail', args=[tectask.id]))

    # Уведомление о запросе продления задачи
    create_notification(tectask.assignee, f'Запрошено продление задачи "{tectask.title}"', 'email', link=tectask_link)
    create_notification(tectask.assignee, f'Запрошено продление задачи "{tectask.title}"', 'telegram', link=tectask_link)

    return redirect('tectask_detail', tectask_id=tectask.id)
