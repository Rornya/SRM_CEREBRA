from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from .models import Assistant
from .forms import AddAssistantForm
from django.contrib.auth.models import User
from tickets.models import Ticket
from tasks.models import Task
from tectasks.models import Tectask
from projects.models import Project
from departments.models import Department
from notifications.utils import create_notification

def add_assistant(request, object_type, object_id):
    # Определяем, с каким объектом работаем
    obj = None
    if object_type == 'ticket':
        obj = get_object_or_404(Ticket, id=object_id)
    elif object_type == 'task':
        obj = get_object_or_404(Task, id=object_id)
    elif object_type == 'tectask':
        obj = get_object_or_404(Tectask, id=object_id)
    else:
        return redirect('home')

    # Получаем отдел из GET-запроса
    department_id = request.GET.get('department')

    if request.method == 'POST':
        form = AddAssistantForm(request.POST)
        if form.is_valid():
            assistant_user = form.cleaned_data['user']

            # Проверка, не является ли пользователь ассистентом, автором или исполнителем
            if Assistant.objects.filter(**{object_type: obj}, user=assistant_user).exists():
                messages.error(request, f'Пользователь {assistant_user.get_full_name()} уже добавлен в ассистенты.')
            elif hasattr(obj, 'assignee') and obj.assignee == assistant_user:
                messages.error(request, f'Пользователь {assistant_user.get_full_name()} является исполнителем и не может быть добавлен в ассистенты.')
            elif hasattr(obj, 'author') and obj.author == assistant_user:
                messages.error(request, f'Пользователь {assistant_user.get_full_name()} является автором и не может быть добавлен в ассистенты.')
            else:
                # Создание ассистента
                Assistant.objects.create(**{object_type: obj}, user=assistant_user)

                # Создание ссылки для уведомления
                obj_link = request.build_absolute_uri(reverse(f'{object_type}_detail', args=[obj.id]))

                # Уведомление для нового ассистента
                create_notification(
                    assistant_user, 
                    f'Вы были добавлены в {object_type.capitalize()}: {obj.title}', 
                    'email', 
                    link=obj_link
                )
                create_notification(
                    assistant_user, 
                    f'Вы были добавлены в {object_type.capitalize()}: {obj.title}', 
                    'telegram', 
                    link=obj_link
                )

                # Переход на страницу с деталями объекта
                if object_type == 'tectask':
                    return redirect('tectask_detail', tectask_id=obj.id)
                elif object_type == 'task':
                    return redirect('task_detail', task_id=obj.id)
                elif object_type == 'ticket':
                    return redirect('ticket_detail', ticket_id=obj.id)
    else:
        # Обновляем форму в случае GET-запроса
        form = AddAssistantForm()

    # Фильтрация пользователей по отделу
    if department_id:
        form.fields['user'].queryset = User.objects.filter(profile__department=department_id)

    # Получаем все отделы для выбора
    departments = Department.objects.all()

    return render(request, 'assistants/add_assistant.html', {
        'form': form,
        object_type: obj,
        'departments': departments,
        'current_department': department_id,
    })

def remove_assistant(request, object_type, object_id, assistant_id):
    # Определяем объект, с которым работаем
    if object_type == 'ticket':
        obj = get_object_or_404(Ticket, id=object_id)
    elif object_type == 'task':
        obj = get_object_or_404(Task, id=object_id)
    elif object_type == 'tectask':
        obj = get_object_or_404(Tectask, id=object_id)
    else:
        messages.error(request, 'Некорректный тип объекта.')
        return redirect('home')

    # Находим ассистента
    assistant = get_object_or_404(Assistant, id=assistant_id, **{object_type: obj})

    # Удаляем ассистента
    assistant.delete()
    messages.success(request, f'Ассистент {assistant.user.get_full_name()} был успешно удален.')

    # Возвращаемся к детальной странице объекта
    if object_type == 'ticket':
        return redirect('ticket_detail', ticket_id=obj.id)
    elif object_type == 'task':
        return redirect('task_detail', task_id=obj.id)
    elif object_type == 'tectask':
        return redirect('tectask_detail', tectask_id=obj.id)