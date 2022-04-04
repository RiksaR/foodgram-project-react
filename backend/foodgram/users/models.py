from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    """Пользовательская модель User
    """

    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'first_name',
        'last_name',
        'username',
        'password',
    ]

    def __str__(self):
        return self.username
