# plataforma-cursos/usuarios/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import timedelta


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El Email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text=_(
            "Opcional. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ únicamente."
        ),
    )
    full_name = models.CharField(_("full name"), max_length=255, blank=True)
    phone = models.CharField(
        _("phone number"),
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message="El número de teléfono debe estar en formato: '+999999999'.",
            )
        ],
    )
    telegram_id = models.CharField(
        _("Telegram ID"), max_length=50, blank=True, null=True
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    preferences = models.JSONField(_("preferences"), default=dict, blank=True)

    # Nuevos campos
    is_email_verified = models.BooleanField(_("email verified"), default=False)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    account_locked_until = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email or self.username or f"User {self.id}"

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
            models.Index(fields=["is_email_verified"]),
        ]

    def get_full_name(self):
        """Retorna el nombre completo del usuario."""
        return (
            self.full_name
            or f"{self.first_name} {self.last_name}".strip()
            or self.email
        )

    def get_short_name(self):
        """Retorna el nombre corto del usuario."""
        return self.first_name or self.email.split("@")[0]

    def get_profile_url(self):
        """Retorna la URL del perfil del usuario."""
        from django.urls import reverse

        return reverse("usuarios:profile", args=[self.id])

    def increment_failed_login_attempts(self):
        """Incrementa el contador de intentos fallidos de inicio de sesión."""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.account_locked_until = timezone.now() + timedelta(minutes=30)
        self.save()

    def reset_failed_login_attempts(self):
        """Reinicia el contador de intentos fallidos."""
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.save()

    def is_account_locked(self):
        """Verifica si la cuenta está bloqueada."""
        if self.account_locked_until and timezone.now() < self.account_locked_until:
            return True
        return False

    def get_active_membership(self):
        return self.memberships.filter(status="active").order_by("-end_date").first()

    @property
    def has_active_membership(self):
        return self.get_active_membership() is not None

    def get_courses(self):
        from cursos.models import Course

        return Course.objects.filter(user_courses__user=self)
