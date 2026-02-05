from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Аутентификация по email или имени пользователя
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        try:
            user = User.objects.get(
                Q(email__iexact=username) | Q(username__iexact=username)
            )


            if user.check_password(password):

                user.backend = 'main.backends.EmailOrUsernameModelBackend'
                return user

        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            user.backend = 'main.backends.EmailOrUsernameModelBackend'
            return user
        except User.DoesNotExist:
            return None


class EmailBackend(ModelBackend):
    """Аутентификация по email"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Пробуем найти пользователя по email
            user = User.objects.get(
                Q(email=username) | Q(username=username)
            )

            # Проверяем пароль
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None