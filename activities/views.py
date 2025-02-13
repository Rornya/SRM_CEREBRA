from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Activity
from .forms import ActivityForm
from notifications.utils import create_notification

@login_required
def activity_list(request):
    activities = Activity.objects.all()
    return render(request, 'activities/activity_list.html', {'activities': activities})

@login_required
def activity_create(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.save()
            form.save_m2m()  # Сохраняем участников
            
            # Рассылка уведомлений участникам
            recipients = form.cleaned_data['participants']
            for recipient in recipients:
                user = recipient.user  # Получаем связанного пользователя
                message = f"Вы приглашены на {activity.title} в {activity.activity_time} {activity.activity_date}"
                link = request.build_absolute_uri(activity.get_absolute_url())
                create_notification(user, message, 'email', link=link)
                create_notification(user, message, 'telegram', link=link)
            
            return redirect('activity_list')
    else:
        form = ActivityForm()
    return render(request, 'activities/activity_form.html', {'form': form})


@login_required
def activity_complete(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    activity.is_completed = True
    activity.save()
    return redirect('activity_list')

@login_required
def activity_delete(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    activity.delete()
    return redirect('activity_list')

def activity_detail(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    return render(request, 'activities/activity_detail.html', {'activity': activity})
