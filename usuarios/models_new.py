# plataforma-cursos/usuarios/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
import re


def validate_strong_password(password):
    """
    Validador personalizado para contraseñas fuertes.
    Requiere al menos: 8 caracteres, 1 mayúscula, 1 minúscula, 1 número y 1 carácter especial.
    """
    if len(password) < 8:
        raise ValidationError(_('La contraseña debe tener al menos 8 caracteres.'))
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError(_('La contraseña debe contener al menos una letra mayúscula.'))
    
    if not re.search(r'[a-z]', password):
        raise ValidationError(_('La contraseña debe contener al menos una letra minúscula.'))
    
    if not re.search(r'\d', password):
        raise ValidationError(_('La contraseña debe contener al menos un número.'))
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>\/?]', password):
        raise ValidationError(_('La contraseña debe contener al menos un carácter especial.'))


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El Email es obligatorio")
        
        # Validar formato de email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError("El formato del email no es válido")
        
        email = self.normalize_email(email)
        
        # Generar username automáticamente si no se proporciona
        if not extra_fields.get('username'):
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            while self.model.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            extra_fields['username'] = username
        
        user = self.model(email=email, **extra_fields)
        if password:
            # Validar contraseña antes de establecerla
            validate_strong_password(password)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_email_verified", True)
        
        if not password:
            raise ValueError("Los superusuarios deben tener una contraseña")
        
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

    # Campos de seguridad
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
        elif self.account_locked_until and timezone.now() >= self.account_locked_until:
            # Desbloquear automáticamente si el tiempo ha expirado
            self.reset_failed_login_attempts()
        return False
    
    def can_login(self):
        """Verifica si el usuario puede iniciar sesión."""
        if not self.is_active:
            return False, "La cuenta está desactivada"
        
        if self.is_account_locked():
            time_left = (self.account_locked_until - timezone.now()).total_seconds() / 60
            return False, f"Cuenta bloqueada. Intenta en {int(time_left)} minutos"
        
        if not self.is_email_verified:
            return False, "Debes verificar tu email antes de iniciar sesión"
        
        return True, "OK"
    
    def set_password(self, raw_password):
        """Override para validar contraseña antes de establecerla."""
        if raw_password:
            validate_strong_password(raw_password)
        super().set_password(raw_password)
    
    def update_last_login_info(self, ip_address=None):
        """Actualiza información del último inicio de sesión."""
        self.last_login = timezone.now()
        if ip_address:
            self.last_login_ip = ip_address
        self.reset_failed_login_attempts()
        self.save()

    def get_active_membership(self):
        """Retorna la membresía activa del usuario."""
        return self.memberships.filter(status="active").order_by("-end_date").first()

    @property
    def has_active_membership(self):
        """Verifica si el usuario tiene una membresía activa."""
        return self.get_active_membership() is not None

    def get_courses(self):
        """Retorna los cursos del usuario."""
        from cursos.models import Course
        return Course.objects.filter(user_courses__user=self)
