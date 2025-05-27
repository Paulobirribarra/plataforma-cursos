# membresias/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from usuarios.models import CustomUser


class MembershipPlan(models.Model):
    """Modelo para los planes de membresía disponibles."""

    name = models.CharField(_("nombre"), max_length=100)
    slug = models.SlugField(_("slug"), unique=True)
    price = models.DecimalField(
        _("precio"), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    courses_per_month = models.IntegerField(
        _("cursos por mes"), validators=[MinValueValidator(0)]
    )
    discount_percentage = models.IntegerField(
        _("porcentaje de descuento"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    consultations = models.IntegerField(
        _("consultas incluidas"), validators=[MinValueValidator(0)]
    )
    telegram_level = models.CharField(
        _("nivel de telegram"),
        max_length=50,
        choices=[
            ("basic", _("Básico")),
            ("intermediate", _("Intermedio")),
            ("premium", _("Premium")),
        ],
    )
    description = models.TextField(_("descripción"))
    features = models.JSONField(_("características"), default=list)
    is_active = models.BooleanField(_("activo"), default=True)
    created_at = models.DateTimeField(_("creado en"), auto_now_add=True)
    updated_at = models.DateTimeField(_("actualizado en"), auto_now=True)

    class Meta:
        verbose_name = _("plan de membresía")
        verbose_name_plural = _("planes de membresía")
        ordering = ["price"]

    def __str__(self):
        return self.name


class Membership(models.Model):
    """Modelo para las membresías de los usuarios."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="memberships",
        verbose_name=_("usuario"),
    )
    plan = models.ForeignKey(
        MembershipPlan,
        on_delete=models.PROTECT,
        related_name="memberships",
        verbose_name=_("plan"),
    )
    start_date = models.DateTimeField(_("fecha de inicio"), default=timezone.now)
    end_date = models.DateTimeField(_("fecha de fin"))
    status = models.CharField(
        _("estado"),
        max_length=20,
        choices=[
            ("active", _("Activa")),
            ("expired", _("Expirada")),
            ("cancelled", _("Cancelada")),
            ("pending", _("Pendiente")),
        ],
        default="pending",
    )
    courses_remaining = models.IntegerField(
        _("cursos restantes"), validators=[MinValueValidator(0)]
    )
    consultations_remaining = models.IntegerField(
        _("consultas restantes"), validators=[MinValueValidator(0)]
    )
    auto_renew = models.BooleanField(_("renovación automática"), default=True)
    created_at = models.DateTimeField(_("creado en"), auto_now_add=True)
    updated_at = models.DateTimeField(_("actualizado en"), auto_now=True)

    class Meta:
        verbose_name = _("membresía")
        verbose_name_plural = _("membresías")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["end_date"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"

    def save(self, *args, **kwargs):
        if not self.end_date:
            # Por defecto, la membresía dura 30 días
            self.end_date = self.start_date + timezone.timedelta(days=30)
        if not self.courses_remaining:
            self.courses_remaining = self.plan.courses_per_month
        if not self.consultations_remaining:
            self.consultations_remaining = self.plan.consultations
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        """Verifica si la membresía está activa."""
        return (
            self.status == "active"
            and self.end_date > timezone.now()
            and self.courses_remaining > 0
        )

    def can_access_course(self):
        """Verifica si el usuario puede acceder a un nuevo curso."""
        return self.is_active and self.courses_remaining > 0

    def can_request_consultation(self):
        """Verifica si el usuario puede solicitar una consulta."""
        return self.is_active and self.consultations_remaining > 0

    def get_available_courses(self):
        """Retorna los cursos disponibles para esta membresía."""
        from cursos.models import Course

        return Course.objects.filter(
            models.Q(membership_required=True)
            & (
                models.Q(available_membership_plans=self.plan)
                | ~models.Q(available_membership_plans__isnull=False)
            )
        ).distinct()

    def can_access_specific_course(self, course):
        """Verifica si la membresía puede acceder a un curso específico."""
        if not self.is_active:
            return False

        if not course.membership_required:
            return True

        if course.available_membership_plans.exists():
            return course.available_membership_plans.filter(id=self.plan.id).exists()

        return self.courses_remaining > 0

    def use_course(self, course):
        """Registra el uso de un curso y actualiza el contador."""
        if not self.can_access_specific_course(course):
            return False

        if not course.available_membership_plans.exists():
            self.courses_remaining -= 1
            self.save()

        # Registrar en el historial
        MembershipHistory.objects.create(
            membership=self,
            action="course_used",
            details={
                "course_id": course.id,
                "course_title": course.title,
                "courses_remaining": self.courses_remaining,
            },
        )
        return True


class MembershipHistory(models.Model):
    """Modelo para el historial de cambios en las membresías."""

    membership = models.ForeignKey(
        Membership,
        on_delete=models.CASCADE,
        related_name="history",
        verbose_name=_("membresía"),
    )
    action = models.CharField(
        _("acción"),
        max_length=50,
        choices=[
            ("created", _("Creada")),
            ("renewed", _("Renovada")),
            ("cancelled", _("Cancelada")),
            ("expired", _("Expirada")),
            ("course_used", _("Curso utilizado")),
            ("consultation_used", _("Consulta utilizada")),
        ],
    )
    details = models.JSONField(_("detalles"), default=dict)
    created_at = models.DateTimeField(_("creado en"), auto_now_add=True)

    class Meta:
        verbose_name = _("historial de membresía")
        verbose_name_plural = _("historiales de membresías")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.membership} - {self.action}"
