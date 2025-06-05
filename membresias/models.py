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
        _("consultas restantes"), default=0, validators=[MinValueValidator(0)]
    )
    
    # Campos para sistema de cursos de recompensa
    has_claimed_welcome_course = models.BooleanField(
        _("ha reclamado curso de bienvenida"), 
        default=False,
        help_text="Indica si el usuario ya reclamó su curso de bienvenida para este ciclo"
    )
    welcome_courses_claimed = models.ManyToManyField(
        "cursos.Course",
        blank=True,
        related_name="claimed_as_welcome",
        verbose_name=_("cursos de bienvenida reclamados"),
        help_text="Cursos que el usuario ha reclamado como recompensa de bienvenida"
    )
    welcome_courses_remaining = models.IntegerField(
        _("cursos de bienvenida restantes"),
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Número de cursos de recompensa que puede reclamar en este ciclo"
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
        
        # Configurar cursos de bienvenida según el plan
        if not hasattr(self, '_skip_welcome_setup'):
            if self.plan.slug == 'basico':
                self.welcome_courses_remaining = 1
            elif self.plan.slug == 'intermedio':
                self.welcome_courses_remaining = 2
            elif self.plan.slug == 'premium':
                self.welcome_courses_remaining = 0  # Premium tiene acceso completo, no necesita cursos de bienvenida
        
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        """Verifica si la membresía está activa."""
        # Para plan Premium (acceso ilimitado), no verificar courses_remaining
        if self.plan.courses_per_month >= 999:
            return (
                self.status == "active"
                and self.end_date > timezone.now()
            )
        
        return (
            self.status == "active"
            and self.end_date > timezone.now()
            and self.courses_remaining > 0
        )

    def can_access_course(self):
        """Verifica si el usuario puede acceder a un nuevo curso."""
        # Para plan Premium (acceso ilimitado), siempre puede acceder si está activo
        if self.plan.courses_per_month >= 999:
            return self.status == "active" and self.end_date > timezone.now()
            
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

        # Para plan Premium (acceso ilimitado), puede acceder a cualquier curso
        if self.plan.courses_per_month >= 999:
            if course.available_membership_plans.exists():
                return course.available_membership_plans.filter(id=self.plan.id).exists()
            return True

        if course.available_membership_plans.exists():
            return course.available_membership_plans.filter(id=self.plan.id).exists()

        return self.courses_remaining > 0

    def use_course(self, course):
        """Registra el uso de un curso y actualiza el contador."""
        if not self.can_access_specific_course(course):
            return False

        # Para plan Premium (acceso ilimitado), no descontar cursos
        if self.plan.courses_per_month >= 999:
            # Solo registrar en el historial, no descontar
            MembershipHistory.objects.create(
                membership=self,
                action="course_used",
                details={
                    "course_id": course.id,
                    "course_title": course.title,
                    "courses_remaining": "ilimitado",
                    "plan_type": "premium"
                },
            )
            return True

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

    def get_available_reward_courses(self):
        """Retorna los cursos de recompensa disponibles para este plan."""
        from cursos.models import Course
        
        return Course.objects.filter(
            is_membership_reward=True,
            reward_for_plans=self.plan,
            is_available=True
        ).exclude(
            id__in=self.welcome_courses_claimed.values_list('id', flat=True)
        )
    
    def can_claim_reward_course(self):
        """Verifica si puede reclamar un curso de recompensa."""
        return self.welcome_courses_remaining > 0 and self.status == 'active'
    
    def claim_reward_course(self, course):
        """Reclama un curso de recompensa."""
        if not self.can_claim_reward_course():
            return False, "No tienes cursos de recompensa disponibles"
        
        if not course.is_membership_reward:
            return False, "Este curso no es una recompensa"
        
        if course not in self.get_available_reward_courses():
            return False, "Este curso no está disponible para tu plan"
        
        # Reclamar el curso
        self.welcome_courses_claimed.add(course)
        self.welcome_courses_remaining -= 1
        self.save()
        
        # Registrar en el historial
        MembershipHistory.objects.create(
            membership=self,
            action="reward_claimed",
            details={
                "course_id": course.id,
                "course_title": course.title,
                "remaining_rewards": self.welcome_courses_remaining,
            },
        )
        
        return True, "Curso de recompensa reclamado exitosamente"


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
            ("course_used", _("Curso usado")),
            ("consultation_used", _("Consulta usada")),
            ("reward_claimed", _("Recompensa reclamada")),
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


class ConsultationType(models.Model):
    """Modelo para tipos de consultas disponibles por membresía."""
    
    name = models.CharField(_("nombre"), max_length=100)
    slug = models.SlugField(_("slug"), unique=True)
    description = models.TextField(_("descripción"))
    is_individual = models.BooleanField(_("es individual"), default=False)
    duration_minutes = models.IntegerField(_("duración en minutos"), default=30)
    membership_plans = models.ManyToManyField(
        MembershipPlan,
        related_name="consultation_types",
        verbose_name=_("planes de membresía"),
        help_text=_("Planes que incluyen este tipo de consulta")
    )
    is_active = models.BooleanField(_("activo"), default=True)
    created_at = models.DateTimeField(_("creado en"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("tipo de consulta")
        verbose_name_plural = _("tipos de consultas")
        ordering = ["name"]
    
    def __str__(self):
        return f"{self.name} ({'Individual' if self.is_individual else 'Grupal'})"


class ConsultationRequest(models.Model):
    """Modelo para solicitudes de consultas."""
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="consultation_requests",
        verbose_name=_("usuario")
    )
    membership = models.ForeignKey(
        Membership,
        on_delete=models.CASCADE,
        related_name="consultation_requests",
        verbose_name=_("membresía")
    )
    consultation_type = models.ForeignKey(
        ConsultationType,
        on_delete=models.CASCADE,
        related_name="requests",
        verbose_name=_("tipo de consulta")
    )
    requested_date = models.DateTimeField(_("fecha solicitada"))
    status = models.CharField(
        _("estado"),
        max_length=20,
        choices=[
            ("pending", _("Pendiente")),
            ("confirmed", _("Confirmada")),
            ("completed", _("Completada")),
            ("cancelled", _("Cancelada")),
        ],
        default="pending"
    )
    notes = models.TextField(_("notas"), blank=True)
    created_at = models.DateTimeField(_("creado en"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("solicitud de consulta")
        verbose_name_plural = _("solicitudes de consultas")
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.user.email} - {self.consultation_type.name}"
