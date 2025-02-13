from django.shortcuts import render
from django.contrib.auth.models import User
from collections import defaultdict

def contact_list(request):
    # Исключаем суперпользователей и сортируем пользователей по имени (фамилии)
    users = User.objects.filter(is_superuser=False).order_by('first_name')
    
    # Группируем пользователей по первой букве имени
    grouped_users = defaultdict(list)
    for user in users:
        first_letter = user.first_name[0].upper()
        grouped_users[first_letter].append(user)
    
    # Возвращаем шаблон с группированными пользователями
    return render(request, 'contacts/contact_list.html', {'grouped_users': dict(grouped_users)})
