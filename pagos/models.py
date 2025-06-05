from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from usuarios.models import CustomUser


class Payment(models.Model):
    """Modelo para gestionar los pagos del sistema."""

    PAYMENT_STATUS = [
        ("pending", _("Pendiente")),
        ("completed", _("Completado")),
        ("failed", _("Fallido")),
        ("cancelled", _("Cancelado")),
    ]

    PAYMENT_TYPES = [
        ("course", _("Curso")),
        ("membership", _("Membresía")),
        ("cart", _("Carrito")),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name=_("usuario"),
    )
    amount = models.DecimalField(_("monto"), max_digits=10, decimal_places=2)
    description = models.CharField(_("descripción"), max_length=255)
    status = models.CharField(
        _("estado"), max_length=20, choices=PAYMENT_STATUS, default="pending"
    )
    payment_type = models.CharField(
        _("tipo de pago"), max_length=20, choices=PAYMENT_TYPES
    )
    transaction_id = models.CharField(
        _("ID de transacción"), max_length=255, null=True, blank=True
    )
    # Campos para la relación genérica
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    created_at = models.DateTimeField(_("creado en"), auto_now_add=True)
    updated_at = models.DateTimeField(_("actualizado en"), auto_now=True)

    class Meta:
        verbose_name = _("pago")
        verbose_name_plural = _("pagos")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.amount} - {self.get_status_display()}"
