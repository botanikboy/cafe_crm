from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pin_code = models.CharField(
        'Пин-код',
        max_length=4,
        blank=True,
        null=True,
        unique=True,
        help_text="Используется для входа в систему смен"
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']
