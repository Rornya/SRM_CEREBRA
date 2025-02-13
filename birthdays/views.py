from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.models import UserProfile

@login_required
def birthdays_list(request):
    # Получаем всех пользователей, у которых указана дата рождения
    birthdays = UserProfile.objects.filter(birth_date__isnull=False).order_by('birth_date')

    return render(request, 'birthdays/birthdays_list.html', {'birthdays': birthdays})
