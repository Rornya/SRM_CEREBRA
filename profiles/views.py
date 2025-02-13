from django.shortcuts import render, get_object_or_404  # Импортируем get_object_or_404
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserProfileForm

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'profiles/profile.html', {'profile': profile})

@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    print(f"Initial Hire Date: {profile.hire_date}, Initial Birthday: {profile.birthday}")  # Отладка

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save()
            print(f"Saved Hire Date: {profile.hire_date}, Saved Birthday: {profile.birthday}")  # Отладка
            return redirect('profile')
        else:
            print(f"Form Errors: {form.errors}")  # Отладка
    else:
        form = UserProfileForm(instance=profile)

        # Явная инициализация для виджетов
        if profile.hire_date:
            form.fields['hire_date'].widget.attrs['value'] = profile.hire_date.strftime('%Y-%m-%d')
        if profile.birthday:
            form.fields['birthday'].widget.attrs['value'] = profile.birthday.strftime('%Y-%m-%d')

    return render(request, 'profiles/edit_profile.html', {'form': form})


@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'profiles/profile.html', {'form': form, 'user_profile': user_profile})

@login_required
def view_user_profile(request, user_id):
    user_profile = get_object_or_404(UserProfile, user_id=user_id)
    is_store_account = request.user.userprofile.is_store_account  # Проверяем статус текущего пользователя

    return render(request, 'profiles/view_user_profile.html', {
        'user_profile': user_profile,
        'is_store_account': is_store_account,
    })