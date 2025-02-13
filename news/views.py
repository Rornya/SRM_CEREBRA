from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .forms import NewsForm
from .models import NewsPost
from django.contrib.auth.models import User
from notifications.utils import create_notification

@login_required
def news_list(request):
    # Определяем роль пользователя из профиля
    user_role = request.user.userprofile.role

    # Фильтрация новостей по булевым полям
    if user_role == 'office':
        news_list = NewsPost.objects.filter(is_visible_for_office=True, is_published=True)
    elif user_role == 'warehouse':
        news_list = NewsPost.objects.filter(is_visible_for_warehouse=True, is_published=True)
    elif user_role == 'store':
        news_list = NewsPost.objects.filter(is_visible_for_store=True, is_published=True)
    else:
        news_list = NewsPost.objects.none()  # Если нет роли, не показываем новости

    # Добавляем новости, созданные автором
    own_news = NewsPost.objects.filter(author=request.user, is_published=True)
    news_list = (news_list | own_news).distinct()

    return render(request, 'news/news_list.html', {'news_list': news_list})

def news_detail(request, news_id):
    news = get_object_or_404(NewsPost, id=news_id, is_published=True)
    return render(request, 'news/news_detail.html', {'news': news})

@login_required
def add_news(request):
    if request.user.userprofile.can_post_news:
        if request.method == 'POST':
            form = NewsForm(request.POST)
            if form.is_valid():
                news_post = form.save(commit=False)
                news_post.author = request.user
                news_post.save()

                # Формируем корректный URL новости
                news_link = request.build_absolute_uri(news_post.get_absolute_url())

                # Формируем список получателей
                recipients = []

                if news_post.is_visible_for_office:
                    recipients += User.objects.filter(userprofile__role='Офис')

                if news_post.is_visible_for_warehouse:
                    recipients += User.objects.filter(userprofile__role='Склад')

                if news_post.is_visible_for_store:
                    recipients += User.objects.filter(userprofile__role='Магазин')

                # Убираем дубликаты
                recipients = set(recipients)

                # Рассылаем уведомления
                for user in recipients:
                    create_notification(user, f'Новое объявление: {news_post.title}', 'email', link=news_link)
                    create_notification(user, f'Новое объявление: {news_post.title}', 'telegram', link=news_link)

                return redirect('news_list')
        else:
            form = NewsForm()
        return render(request, 'news/add_news.html', {'form': form})
    else:
        return redirect('news_list')


@login_required
def edit_news(request, news_id):
    news = get_object_or_404(NewsPost, id=news_id)
    if request.user.userprofile.can_edit_news:  # Проверяем права пользователя
        if request.method == 'POST':
            form = NewsForm(request.POST, instance=news)
            if form.is_valid():
                news_post = form.save()

                # Обновляем уведомления только если нужно
                send_notification(news_post, request)

                return redirect('news_detail', news_id=news.id)
        else:
            form = NewsForm(instance=news)
        return render(request, 'news/edit_news.html', {'form': form, 'news': news})
    else:
        return redirect('news_list')  # Если нет прав, перенаправляем на список новостей
