#plataforma-cursos/usuarios/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text=_('Opcional. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ únicamente.'),
    )
    full_name = models.CharField(_('full name'), max_length=255, blank=True)
    phone = models.CharField(_('phone number'), max_length=20, blank=True, null=True)
    telegram_id = models.CharField(_('Telegram ID'), max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    preferences = models.JSONField(_('preferences'), default=dict, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email or self.username or f"User {self.id}"

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
        ]