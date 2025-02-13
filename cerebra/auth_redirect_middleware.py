from django.shortcuts import redirect
from django.conf import settings

class AuthRedirectMiddleware:
    """
    Middleware to redirect unauthenticated users to the login page.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Проверяем, что пользователь не авторизован и запрашивает защищённый URL
        if not request.user.is_authenticated and not request.path.startswith(settings.LOGIN_URL):
            # Добавляем параметр "next" для перенаправления обратно после логина
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")
        return self.get_response(request)
