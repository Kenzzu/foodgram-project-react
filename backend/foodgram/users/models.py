from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.settings import AUTH_USER_MODEL


class User(AbstractUser):

    email = models.EmailField(
        'E-mail address',
        unique=True,
        max_length=254,
    )
    username = models.CharField(
        'Username',
        unique=True,
        max_length=150,
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
    )
    password = models.CharField(
        'Пароль',
        max_length=150,
    )
    is_blocked = models.BooleanField(
        default=False, verbose_name='Блокировка')

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Follow(models.Model):
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор контента',
    )

    class Meta:
        ordering = ('user',)
        unique_together = ('user', 'author')
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписчики'
