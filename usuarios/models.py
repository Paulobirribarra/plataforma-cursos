from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = None

    SUBSCRIPTION_LEVELS = (
        ('basic', 'Básico'),
        ('intermediate', 'Intermedio'),
        ('premium', 'Premium'),
    )
    subscription_level = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_LEVELS,
        default='basic',
        verbose_name="Nivel de Suscripción"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email