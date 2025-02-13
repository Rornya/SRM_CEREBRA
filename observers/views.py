from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Observer
from tickets.models import Ticket
from tasks.models import Task
from tectasks.models import Tectask
from projects.models import Project
from .forms import ObserverForm

# Вьюха для добавления наблюдателя к заявке
@login_required
def add_observer_to_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        form = ObserverForm(request.POST)
        if form.is_valid():
            observer = form.save(commit=False)
            observer.ticket = ticket
            observer.save()
            return redirect('ticket_detail', ticket_id=ticket.id)
    else:
        form = ObserverForm()
    return render(request, 'observers/add_observer_to_ticket.html', {'form': form, 'ticket': ticket})

# Вьюха для добавления наблюдателя к задаче
@login_required
def add_observer_to_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        form = ObserverForm(request.POST)
        if form.is_valid():
            observer = form.save(commit=False)
            observer.task = task
            observer.save()
            return redirect('task_detail', task_id=task.id)
    else:
        form = ObserverForm()
    return render(request, 'observers/add_observer_to_task.html', {'form': form, 'task': task})

# Вьюха для добавления наблюдателя к текущей задаче (tectask)
@login_required
def add_observer_to_tectask(request, tectask_id):
    tectask = get_object_or_404(Tectask, id=tectask_id)
    if request.method == 'POST':
        form = ObserverForm(request.POST)
        if form.is_valid():
            observer = form.save(commit=False)
            observer.tectask = tectask
            observer.save()
            return redirect('tectask_detail', tectask_id=tectask.id)
    else:
        form = ObserverForm()
    return render(request, 'observers/add_observer_to_tectask.html', {'form': form, 'tectask': tectask})

# Вьюха для добавления наблюдателя к проекту
@login_required
def add_observer_to_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = ObserverForm(request.POST)
        if form.is_valid():
            observer = form.save(commit=False)
            observer.project = project
            observer.save()
            return redirect('project_detail', project_id=project.id)
    else:
        form = ObserverForm()
    return render(request, 'observers/add_observer_to_project.html', {'form': form, 'project': project})
