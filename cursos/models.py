from django.db import models
from django.conf import settings
from datetime import timedelta

class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descripción")
    is_available = models.BooleanField(default=False, verbose_name="Disponible")
    is_visible = models.BooleanField(default=False, verbose_name="Visible")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Creado por"
    )
    duration = models.DurationField(
        null=True,
        blank=True,
        default=timedelta(0),
        verbose_name="Duración"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=0.00,
        verbose_name="Precio"
    )
    discount_basic = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Descuento Suscripción Básica (%)"
    )
    discount_intermediate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Descuento Suscripción Intermedia (%)"
    )
    discount_premium = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Descuento Suscripción Premium (%)"
    )
    discount_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Código de Descuento"
    )
    discount_code_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Porcentaje Descuento Código (%)"
    )
    document = models.FileField(
        upload_to='course_documents/',
        blank=True,
        null=True,
        verbose_name="Documento del Curso"
    )
    external_link = models.URLField(
        blank=True,
        null=True,
        verbose_name="Enlace Externo"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"