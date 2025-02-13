from django.core.mail import send_mail
import requests
from .models import Notification

def send_email_notification(subject, message, recipient_list, link=None):
    if link:
        message += f"\n\nПерейти: {link}"
    send_mail(
        subject,
        message,
        'crm@fix-uzb.com',  # От кого будет отправлено письмо
        recipient_list,  # Кому отправляем
        fail_silently=False,
    )

def send_telegram_notification(notification, link=None):
    bot_token = '7320599152:AAERCX1GcThAUzosoVPi2il4v4M2KSxwcGc'
    chat_id = notification.user.userprofile.telegram_chat_ID  # Предполагается, что Telegram ID хранится в профиле пользователя
    text = notification.message
    if link:
        text += f"\nСсылка: {link}"
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={text}'
    response = requests.get(url)
    if response.status_code == 200:
        notification.is_sent = True
        notification.save()

def create_notification(user, message, notification_type, link=None):
    notification = Notification.objects.create(
        user=user,
        message=message,
        notification_type=notification_type,
        link=link
    )
    
    if notification_type == 'email':
        send_email_notification(f'Уведомление для {user.get_full_name()}', message, [user.email], link=link)
    elif notification_type == 'telegram':
        send_telegram_notification(notification, link=link)
