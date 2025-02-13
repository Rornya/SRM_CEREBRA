from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Ticket, TicketChatMessage
from assistants.models import Assistant
from .forms import TicketChatMessageForm, TicketCreationForm, AddAssistantForm, TicketUpdateForm
from departments.models import Department 
from attachments.forms import AttachmentForm
from notifications.utils import create_notification
from django.utils import timezone
from datetime import timedelta
from datetime import datetime
from django.db.models import Q  # Добавляем этот импорт
from django.urls import reverse
from django.contrib import messages
from users.models import UserProfile 
from django.db.models import Case, When, IntegerField

def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    chat_messages = ticket.chat_messages.all()

    form = TicketChatMessageForm()  # форма для чата
    attachment_form = AttachmentForm()  # форма для загрузки файлов
    assistant_form = AddAssistantForm()  # форма для добавления ассистента
    assistants = Assistant.objects.filter(ticket=ticket)  # Получаем всех ассистентов для этой заявки

    ticket_link = request.build_absolute_uri(reverse('ticket_detail', args=[ticket.id]))

    if request.method == 'POST':
        if 'add_message' in request.POST:
            form = TicketChatMessageForm(request.POST)
            if form.is_valid():
                chat_message = form.save(commit=False)
                chat_message.ticket = ticket
                chat_message.user = request.user
                chat_message.save()

                recipients = [ticket.assignee, ticket.author]
                if ticket.observer:
                    recipients.append(ticket.observer)
                for assistant in assistants:
                    recipients.append(assistant.user)

                for recipient in recipients:
                    create_notification(recipient, f'{request.user} написал сообщение в чате заявки: {ticket.title}', 'email', link=ticket_link)
                    create_notification(recipient, f'{request.user} написал сообщение в чате заявки: {ticket.title}', 'telegram', link=ticket_link)

                return redirect('ticket_detail', ticket_id=ticket.id)

        elif 'complete_early' in request.POST and request.user == ticket.author:
            ticket.status = 'completed_early'
            ticket.closed_at = timezone.now()
            ticket.save()

            create_notification(ticket.assignee, f'Заявка "{ticket.title}" завершена автором досрочно.', 'email', link=ticket_link)
            create_notification(ticket.assignee, f'Заявка "{ticket.title}" завершена автором досрочно.', 'telegram', link=ticket_link)

            return redirect('ticket_detail', ticket_id=ticket.id)

        elif 'upload_file' in request.POST:
            attachment_form = AttachmentForm(request.POST, request.FILES)
            if attachment_form.is_valid():
                attachment = attachment_form.save(commit=False)
                attachment.ticket = ticket
                attachment.uploaded_by = request.user
                attachment.save()

                recipients = [ticket.assignee, ticket.author]
                if ticket.observer:
                    recipients.append(ticket.observer)
                for assistant in assistants:
                    recipients.append(assistant.user)

                for recipient in recipients:
                    create_notification(recipient, f'{request.user} добавил файл к заявке: {ticket.title}', 'email', link=ticket_link)
                    create_notification(recipient, f'{request.user} добавил файл к заявке: {ticket.title}', 'telegram', link=ticket_link)

                return redirect('ticket_detail', ticket_id=ticket.id)

        elif 'add_assistant' in request.POST:
            assistant_form = AddAssistantForm(request.POST)
            if assistant_form.is_valid():
                assistant_user = assistant_form.cleaned_data['user']
                Assistant.objects.create(ticket=ticket, user=assistant_user)

                create_notification(assistant_user, f'Вы были добавлены в заявку: {ticket.title}', 'email', link=ticket_link)
                create_notification(assistant_user, f'Вы были добавлены в заявку: {ticket.title}', 'telegram', link=ticket_link)

                return redirect('ticket_detail', ticket_id=ticket.id)

        elif 'confirm_completion' in request.POST:
            ticket.status = 'completed'
            ticket.save()

            create_notification(ticket.assignee, f'Заявка "{ticket.title}" была подтверждена автором как завершенная.', 'email', link=ticket_link)
            create_notification(ticket.assignee, f'Заявка "{ticket.title}" была подтверждена автором как завершенная.', 'telegram', link=ticket_link)

            return redirect('ticket_detail', ticket_id=ticket.id)

        elif 'complete_ticket' in request.POST:
            ticket.status = 'done'
            ticket.save()

            create_notification(ticket.author, f'Заявка "{ticket.title}" завершена и ожидает вашего подтверждения.', 'email', link=ticket_link)
            create_notification(ticket.author, f'Заявка "{ticket.title}" завершена и ожидает вашего подтверждения.', 'telegram', link=ticket_link)

            return redirect('ticket_detail', ticket_id=ticket.id)

        elif 'request_extension' in request.POST:
            extension_date = request.POST.get('extension_date')
            if extension_date and (request.user == ticket.assignee or request.user in ticket.assistants.all()):
                ticket.requested_extension_date = datetime.strptime(extension_date, "%Y-%m-%d").date()
                ticket.status = 'extension_requested'
                ticket.save()

                return redirect('ticket_detail', ticket_id=ticket.id)


        elif 'approve_extension' in request.POST and request.user == ticket.author:
            new_deadline = request.POST.get('extension_date')
            if new_deadline:
                ticket.deadline = datetime.strptime(new_deadline, "%Y-%m-%d").date()
            ticket.status = 'in_progress'
            ticket.save()

            create_notification(ticket.assignee, f'Продление заявки "{ticket.title}" подтверждено автором до {ticket.deadline}', 'email', link=ticket_link)
            create_notification(ticket.assignee, f'Продление заявки "{ticket.title}" подтверждено автором до {ticket.deadline}', 'telegram', link=ticket_link)

            return redirect('ticket_detail', ticket_id=ticket.id)

        elif 'deny_extension' in request.POST and request.user == ticket.author:
            ticket.status = 'in_progress'
            ticket.save()

            create_notification(ticket.assignee, f'Продление заявки "{ticket.title}" было отклонено автором.', 'email', link=ticket_link)
            create_notification(ticket.assignee, f'Продление заявки "{ticket.title}" было отклонено автором.', 'telegram', link=ticket_link)

            return redirect('ticket_detail', ticket_id=ticket.id)

        elif 'return_for_revision' in request.POST:  # Обработка возврата на доработку
            ticket.status = 'in_revision'
            ticket.return_count += 1
            ticket.save()

            create_notification(ticket.assignee, f'Заявка "{ticket.title}" была возвращена на доработку.', 'email', link=ticket_link)
            create_notification(ticket.assignee, f'Заявка "{ticket.title}" была возвращена на доработку.', 'telegram', link=ticket_link)

            if ticket.observer:
                create_notification(ticket.observer, f'Заявка "{ticket.title}" была возвращена на доработку.', 'email', link=ticket_link)
                create_notification(ticket.observer, f'Заявка "{ticket.title}" была возвращена на доработку.', 'telegram', link=ticket_link)

            for assistant in ticket.assistants.all():
                create_notification(assistant.user, f'Заявка "{ticket.title}" была возвращена на доработку.', 'email', link=ticket_link)
                create_notification(assistant.user, f'Заявка "{ticket.title}" была возвращена на доработку.', 'telegram', link=ticket_link)

            return redirect('ticket_detail', ticket_id=ticket.id)

    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket,
        'form': form,
        'attachment_form': attachment_form,
        'assistant_form': assistant_form,
        'chat_messages': chat_messages,
        'assistants': assistants
    })

def ticket_create(request):
    # Фильтрация исполнителей по отделу
    if request.GET.get('department_id'):
        department_id = request.GET.get('department_id')
        assignees = UserProfile.objects.filter(department_id=department_id)
        data = [{'id': user.id, 'full_name': user.user.get_full_name()} for user in assignees]
        return JsonResponse({'assignees': data})

    if request.method == 'POST':
        form = TicketCreationForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.author = request.user

            # Устанавливаем дедлайн по умолчанию, если он не задан
            if not ticket.deadline:
                ticket.deadline = timezone.now() + timedelta(days=3)

            ticket.save()

            # Устанавливаем наблюдателя, если выбран
            observer = form.cleaned_data.get('observers')
            if observer:
                ticket.observers.set([observer])  # Устанавливаем наблюдателя в созданной заявке

            # Создаем ссылки на детальное отображение заявки
            ticket_link = request.build_absolute_uri(reverse('ticket_detail', args=[ticket.id]))

            # Уведомления для исполнителя и автора
            create_notification(ticket.assignee, f'Вам назначена новая заявка: {ticket.title}', 'email', link=ticket_link)
            create_notification(ticket.assignee, f'Вам назначена новая заявка: {ticket.title}', 'telegram', link=ticket_link)
            create_notification(ticket.author, f'Вы создали заявку: {ticket.title}', 'email', link=ticket_link)
            create_notification(ticket.author, f'Вы создали заявку: {ticket.title}', 'telegram', link=ticket_link)

            # Уведомления для наблюдателя, если он добавлен
            if observer:
                create_notification(observer.user, f'Вы наблюдатель заявки: {ticket.title}', 'email', link=ticket_link)
                create_notification(observer.user, f'Вы наблюдатель заявки: {ticket.title}', 'telegram', link=ticket_link)

            return redirect('ticket_detail', ticket_id=ticket.id)
    else:
        form = TicketCreationForm()
    
    # Получаем только учетные записи с флагом full_statistics
    observer_users = UserProfile.objects.filter(full_statistics=True)
    departments = Department.objects.all()
    
    return render(request, 'tickets/ticket_create.html', {
        'form': form,
        'departments': departments,
        'observer_users': observer_users,  # Передаем список наблюдателей в шаблон
    })

def ticket_update(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        form = TicketUpdateForm(request.POST, instance=ticket)
        if form.is_valid():
            ticket = form.save()

            ticket_link = request.build_absolute_uri(reverse('ticket_detail', args=[ticket.id]))

            # Уведомления для всех участников заявки
            notifications = [
                (ticket.assignee, f'Заявка "{ticket.title}" была обновлена.'),
                (ticket.author, f'Заявка "{ticket.title}" была обновлена.'),
            ]

            if ticket.observer:
                notifications.append((ticket.observer, f'Заявка "{ticket.title}" была обновлена.'))

            if ticket.assistants.exists():
                notifications.extend([(assistant, f'Заявка "{ticket.title}" была обновлена.') for assistant in ticket.assistants.all()])

            for user, message in notifications:
                create_notification(user, message, 'email', link=ticket_link)
                create_notification(user, message, 'telegram', link=ticket_link)

            # Перенаправляем на страницу детали заявки
            return redirect('ticket_detail', ticket_id=ticket.id)
        else:
            print(f"Form Errors: {form.errors}")  # Для отладки ошибок
    else:
        form = TicketUpdateForm(instance=ticket)

        # Инициализация значений
        if ticket.deadline:
            form.fields['deadline'].initial = ticket.deadline.strftime('%Y-%m-%d')
            print(f"Deadline Initialized: {form.fields['deadline'].initial}")  # Для отладки

        if not ticket.status:
            form.fields['status'].initial = 'Ожидание'  # Установите значение по умолчанию

    return render(request, 'tickets/ticket_update.html', {'form': form, 'ticket': ticket})


def ticket_list(request):
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

    # Фильтруем заявки, связанные с пользователем
    tickets = Ticket.objects.filter(
        Q(assignee=user) | 
        Q(author=user) | 
        Q(observer=user) | 
        Q(assistants__user=user)
    ).distinct()

    if query:
        tickets = tickets.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    if year:
        tickets = tickets.filter(created_at__year=year)
    if month:
        tickets = tickets.filter(created_at__month=month)

    active_tickets = tickets.exclude(status__in=['completed', 'completed_early']).order_by('-created_at')
    completed_tickets = tickets.filter(status__in=['completed', 'completed_early']).order_by('-created_at')

    # Доступные годы и месяцы
    years = Ticket.objects.dates('created_at', 'year', order='DESC')
    months = {
        1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель', 5: 'Май', 6: 'Июнь',
        7: 'Июль', 8: 'Август', 9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
    }

    return render(request, 'tickets/ticket_list.html', {
        'active_tickets': active_tickets,
        'completed_tickets': completed_tickets,
        'query': query,
        'years': years,
        'months': months,
        'selected_year': year,
        'selected_month': month,
    })

def ticket_return_for_revision(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        # Возвращаем заявку на доработку и меняем статус
        ticket.status = 'in_revision'
        ticket.return_count += 1
        ticket.save()

        ticket_link = request.build_absolute_uri(reverse('ticket_detail', args=[ticket.id]))

        # Уведомления для всех участников заявки
        create_notification(ticket.assignee, f'Заявка "{ticket.title}" была возвращена на доработку.', 'email', link=ticket_link)
        create_notification(ticket.assignee, f'Заявка "{ticket.title}" была возвращена на доработку.', 'telegram', link=ticket_link)

        if ticket.observer:
            create_notification(ticket.observer, f'Заявка "{ticket.title}" была возвращена на доработку.', 'email', link=ticket_link)
            create_notification(ticket.observer, f'Заявка "{ticket.title}" была возвращена на доработку.', 'telegram', link=ticket_link)

        for assistant in ticket.assistants.all():
            create_notification(assistant.user, f'Заявка "{ticket.title}" была возвращена на доработку.', 'email', link=ticket_link)
            create_notification(assistant.user, f'Заявка "{ticket.title}" была возвращена на доработку.', 'telegram', link=ticket_link)

        return redirect('ticket_detail', ticket_id=ticket.id)

    return redirect('ticket_detail', ticket_id=ticket.id)

def accept_ticket(request, ticket_id):
    print("Принятие заявки вызвано")  # Для отладки
    ticket = get_object_or_404(Ticket, id=ticket_id)
    ticket.status = 'in_progress'
    ticket.save()

    ticket_link = request.build_absolute_uri(reverse('ticket_detail', args=[ticket.id]))

    # Уведомление о принятии заявки
    create_notification(ticket.assignee, f'Вы приняли заявку "{ticket.title}"', 'email', link=ticket_link)
    create_notification(ticket.assignee, f'Вы приняли заявку "{ticket.title}"', 'telegram', link=ticket_link)

    return redirect('ticket_detail', ticket_id=ticket.id)

def complete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    ticket.status = 'done'
    ticket.save()

    ticket_link = request.build_absolute_uri(reverse('ticket_detail', args=[ticket.id]))

    # Уведомление автору о завершении заявки
    create_notification(ticket.author, f'Заявка "{ticket.title}" завершена и ожидает вашего подтверждения.', 'email', link=ticket_link)
    create_notification(ticket.author, f'Заявка "{ticket.title}" завершена и ожидает вашего подтверждения.', 'telegram', link=ticket_link)

    return redirect('ticket_detail', ticket_id=ticket.id)

def request_extension_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    ticket.status = 'extension_requested'
    ticket.save()

    ticket_link = request.build_absolute_uri(reverse('ticket_detail', args=[ticket.id]))

    # Уведомление о запросе продления заявки
    create_notification(ticket.assignee, f'Запрошено продление заявки "{ticket.title}"', 'email', link=ticket_link)
    create_notification(ticket.assignee, f'Запрошено продление заявки "{ticket.title}"', 'telegram', link=ticket_link)

    return redirect('ticket_detail', ticket_id=ticket.id)

@login_required
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.user == ticket.author or request.user.has_perm('tickets.delete_ticket'):
        ticket.delete()
        return redirect('tickets_list')

@login_required
def edit_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.user != ticket.author:
        messages.error(request, "У вас нет прав для редактирования этой заявки.")
        return redirect('ticket_detail', ticket_id=ticket.id)

    if request.method == 'POST':
        form = TicketCreationForm(request.POST, instance=ticket)  # Используем форму создания с объектом
        if form.is_valid():
            form.save()
            messages.success(request, "Заявка успешно отредактирована.")
            return redirect('ticket_detail', ticket_id=ticket.id)
    else:
        form = TicketCreationForm(instance=ticket)  # Загружаем данные заявки для редактирования

    return render(request, 'tickets/ticket_create.html', {'form': form, 'ticket': ticket})

def complete_ticket_early(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == "POST" and request.user == ticket.author:
        ticket.status = 'completed_early'
        ticket.closed_at = timezone.now()
        ticket.save()
        ticket_link = request.build_absolute_uri(reverse('ticket_detail', args=[ticket.id]))
        create_notification(ticket.assignee, f'Заявка "{ticket.title}" завершена автором досрочно.', 'email', link=ticket_link)
        return redirect('ticket_detail', ticket_id=ticket.id)
