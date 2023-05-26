from django.core.validators import MinLengthValidator, RegexValidator
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


def password_validation(value):
    validators = [
        MinLengthValidator(
            8, 'Пароль должен содержать не менее 8 символов.'),
        RegexValidator(
            regex=r'^(?=.*[A-Za-z])(?=.*\d).+$',
            message='Пароль должен содержать как '
                    'минимум одну букву и одну цифру.')
    ]
    for validator in validators:
        validator(value)
