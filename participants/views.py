from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Participant
from .forms import AddParticipantsForm
from projects.models import Project
from departments.models import Department
from notifications.utils import create_notification
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def add_participant_to_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    department_id = request.GET.get('department')  # Получаем выбранный отдел
    departments = Department.objects.all().order_by('name')  # Список всех отделов

    if request.method == 'POST':
        # Передаем отдел в форму
        form = AddParticipantsForm(request.POST, department=department_id)
        if form.is_valid():
            users = form.cleaned_data['users']
            for user in users:
                if not Participant.objects.filter(project=project, user=user).exists():
                    Participant.objects.create(project=project, user=user, role="Участник")
                    create_notification(user, f'Вы добавлены в проект "{project.title}".', 'email')
                    create_notification(user, f'Вы добавлены в проект "{project.title}".', 'telegram')

            messages.success(request, 'Участники успешно добавлены.')
            return redirect('project_detail', project_id=project.id)
    else:
        # Передаем отдел в форму для GET-запроса
        form = AddParticipantsForm(department=department_id)
        if department_id:
            # Сортируем пользователей по полю `first_name`
            users = User.objects.filter(userprofile__department_id=department_id).order_by('first_name')
            form.fields['users'].queryset = users  # Передача отсортированного списка в форму

    return render(request, 'participants/add_participant.html', {
        'form': form,
        'project': project,
        'departments': departments,
        'current_department': department_id,
    })
