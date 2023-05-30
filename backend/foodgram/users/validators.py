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
    if not value.isalpha():
        raise ValidationError('Имя или фамилия должны содержать только буквы!')


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
