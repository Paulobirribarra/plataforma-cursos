# cursos/models.py
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import timedelta


class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        indexes = [
            models.Index(fields=["name"]),
        ]


class Tag(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Etiqueta"
        verbose_name_plural = "Etiquetas"
        indexes = [
            models.Index(fields=["name"]),
        ]


class Course(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descripción")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name="Categoría",
    )
    base_price = models.IntegerField(default=0, verbose_name="Precio Base (CLP)")
    is_free = models.BooleanField(default=False, verbose_name="Gratuito para todos")
    is_membership_reward = models.BooleanField(
        default=False,
        verbose_name="Curso de recompensa por membresía",
        help_text="Este curso está disponible como recompensa al pagar una membresía",
    )
    is_available = models.BooleanField(default=True, verbose_name="Disponible")
    is_visible = models.BooleanField(default=True, verbose_name="Visible")
    duration_minutes = models.IntegerField(
        default=0,
        verbose_name="Duración (minutos)",
        help_text="Ingrese la duración en minutos (ejemplo: 120 para 2 horas)",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_courses",
        verbose_name="Creado por",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )
    tags = models.ManyToManyField(
        Tag, blank=True, related_name="courses", verbose_name="Etiquetas"
    )
    rating = models.FloatField(default=0.0, verbose_name="Calificación", blank=True)
    special_discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Descuento Especial (%)",
        help_text="Descuento (hasta 15%) para usuarios que reclaman todos los cursos gratuitos.",
    )
    membership_required = models.BooleanField(
        default=False,
        verbose_name="Requiere Membresía",
        help_text="Si está marcado, solo los usuarios con membresía activa pueden acceder",
    )
    available_membership_plans = models.ManyToManyField(
        "membresias.MembershipPlan",
        blank=True,
        related_name="available_courses",
        verbose_name="Planes de Membresía Disponibles",
        help_text="Planes de membresía que pueden acceder a este curso",
    )
    reward_for_plans = models.ManyToManyField(
        "membresias.MembershipPlan",
        blank=True,
        related_name="reward_courses",
        verbose_name="Disponible como recompensa para estos planes",
        help_text="Planes que pueden reclamar este curso como recompensa de bienvenida",
    )

    def clean(self):
        # Asegurarnos de que base_price no sea None
        if self.base_price is None:
            self.base_price = 0

        # Asegurarnos de que special_discount_percentage no sea None
        if self.special_discount_percentage is None:
            self.special_discount_percentage = 0.00

        # Asegurarnos de que duration_minutes no sea None
        if self.duration_minutes is None:
            self.duration_minutes = 0

        # Validaciones
        if self.is_free and self.base_price > 0:
            raise ValidationError("Un curso gratuito debe tener un precio base de 0.")
        if not self.is_free and (not self.base_price or self.base_price <= 0):
            raise ValidationError(
                "Un curso no gratuito debe tener un precio base mayor a 0."
            )
        if self.created_by and not self.created_by.is_staff:
            raise ValidationError(
                "Solo usuarios con permisos de staff pueden crear cursos."
            )
        if (
            self.special_discount_percentage > 15
            or self.special_discount_percentage < 0
        ):
            raise ValidationError("El descuento especial debe estar entre 0% y 15%.")
        if self.duration_minutes < 0:
            raise ValidationError("La duración no puede ser negativa.")

    @property
    def duration(self):
        return timedelta(minutes=self.duration_minutes)

    def get_final_discount(self, discount_code=None):
        special_discount = self.special_discount_percentage or 0
        code_discount = 0
        if discount_code:
            try:
                code = self.discount_codes.get(code__iexact=discount_code)
                code_discount = code.discount_percentage or 0
            except DiscountCode.DoesNotExist:
                pass
        return max(special_discount, code_discount)

    def get_final_price(self, discount_code=None):
        if self.is_free:
            return 0
        discount_percentage = self.get_final_discount(discount_code)
        discount_amount = (self.base_price * discount_percentage) / 100
        return int(self.base_price - discount_amount)

    def can_user_access(self, user):
        """Verifica si un usuario puede acceder al curso."""
        # Si el curso es gratuito, cualquier usuario puede acceder
        if self.is_free:
            return True

        # Si el usuario ya tiene acceso al curso
        if self.user_courses.filter(user=user, completed=False).exists():
            return True

        # Si el curso requiere membresía
        if self.membership_required:
            active_membership = user.get_active_membership()
            if not active_membership:
                return False
            if self.available_membership_plans.exists():
                return self.available_membership_plans.filter(
                    id=active_membership.plan.id
                ).exists()
            return active_membership.can_access_course()

        return True

    def get_available_membership_plans(self):
        """Retorna los planes de membresía que pueden acceder al curso."""
        if not self.membership_required:
            return None
        return self.available_membership_plans.filter(is_active=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["category"]),
            models.Index(fields=["membership_required"]),
        ]


class CourseResource(models.Model):
    RESOURCE_TYPES = (
        ("video", "Video"),
        ("pdf", "PDF"),
        ("link", "Enlace"),
    )
    id = models.BigAutoField(primary_key=True)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="resources", verbose_name="Curso"
    )
    title = models.CharField(max_length=200, verbose_name="Título")
    file = models.FileField(
        upload_to="course_resources/", blank=True, null=True, verbose_name="Archivo"
    )
    url = models.URLField(blank=True, null=True, verbose_name="URL")
    type = models.CharField(max_length=20, choices=RESOURCE_TYPES, verbose_name="Tipo")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )

    def clean(self):
        if not self.file and not self.url:
            raise ValidationError("Debe proporcionar un archivo o una URL.")
        if self.file and self.url:
            raise ValidationError(
                "No puede proporcionar tanto un archivo como una URL."
            )

    def __str__(self):
        return f"{self.title} ({self.get_type_display()})"

    class Meta:
        verbose_name = "Recurso del Curso"
        verbose_name_plural = "Recursos del Curso"


class UserCourse(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_courses",
        verbose_name="Usuario",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="user_courses",
        verbose_name="Curso",
    )
    access_start = models.DateTimeField(
        auto_now_add=True, verbose_name="Inicio de Acceso"
    )
    access_end = models.DateTimeField(
        blank=True, null=True, verbose_name="Fin de Acceso"
    )
    progress = models.FloatField(default=0.0, verbose_name="Progreso (%)")
    completed = models.BooleanField(default=False, verbose_name="Completado")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )

    def __str__(self):
        return f"{self.user.email} - {self.course.title}"

    class Meta:
        verbose_name = "Acceso a Curso"
        verbose_name_plural = "Accesos a Cursos"
        unique_together = ["user", "course"]
        indexes = [
            models.Index(fields=["user", "course"]),
        ]


class DiscountCode(models.Model):
    id = models.BigAutoField(primary_key=True)
    course = models.ForeignKey(
        Course,        on_delete=models.CASCADE,
        related_name="discount_codes",
        verbose_name="Curso",
    )
    code = models.CharField(
        max_length=50, unique=True, verbose_name="Código de Descuento"
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Porcentaje de Descuento (%)",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )

    def clean(self):
        if self.discount_percentage is None:
            self.discount_percentage = 0.00

        if self.discount_percentage < 0 or self.discount_percentage > 100:
            raise ValidationError(
                "El porcentaje de descuento debe estar entre 0 y 100."
            )
        
        # Solo validar si el curso ya está asignado (para evitar errores en formularios)
        if self.course_id and hasattr(self, 'course') and self.course.is_free and self.discount_percentage > 0:
            raise ValidationError("No se pueden aplicar descuentos a cursos gratuitos.")

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} ({self.discount_percentage}%) para {self.course.title}"

    class Meta:
        verbose_name = "Código de Descuento"
        verbose_name_plural = "Códigos de Descuento"
        indexes = [
            models.Index(fields=["course"]),
            models.Index(fields=["code"]),
        ]



