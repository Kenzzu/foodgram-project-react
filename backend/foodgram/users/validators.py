from rest_framework.exceptions import ValidationError

from .models import User


def username_validation(value):
    """Проверка имени пользователя."""
    if value.lower() in ['me', 'set_password', 'subscriptions', 'subscribe']:
        raise ValidationError('Недопустимое имя пользователя!')
    if User.objects.filter(username=value).exists():
        raise ValidationError(
            f'Пользователь с именем {value} уже зарегистрирован!'
        )


def email_validation(value):
    """Проверка адреса электронной почты пользователя."""
    if User.objects.filter(email=value).exists():
        raise ValidationError(
            f'Пользователь с почтой {value} '
            'уже зарегистрирован!'
        )


def name_validation(value):
    """Проверка имени и фамилии пользователя."""
    if any(char.isdigit() for char in value):
        raise ValidationError('Имя или фамилия не должно содержать цифры!')
