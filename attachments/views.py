from django.shortcuts import render, redirect, get_object_or_404
from .forms import AttachmentForm
from .models import Attachment
from projects.models import Project
from tasks.models import Task
from tickets.models import Ticket

def upload_attachment(request, project_id=None, task_id=None, ticket_id=None):
    if request.method == 'POST':
        form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.uploaded_by = request.user
            if project_id:
                project = get_object_or_404(Project, id=project_id)
                attachment.project = project
            elif task_id:
                task = get_object_or_404(Task, id=task_id)
                attachment.task = task
            elif ticket_id:
                ticket = get_object_or_404(Ticket, id=ticket_id)
                attachment.ticket = ticket
            attachment.save()
            return redirect('some_detail_view')  # Переадресация на нужную страницу
    else:
        form = AttachmentForm()

    return render(request, 'attachments/upload_attachment.html', {'form': form})
