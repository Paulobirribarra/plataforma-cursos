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
        ("rejected", _("Rechazado")),
        ("timeout", _("Tiempo Agotado")),
        ("nullified", _("Anulado")),
        ("error", _("Error del Sistema")),
    ]

    PAYMENT_TYPES = [
        ("course", _("Curso")),
        ("membership", _("Membresía")),
        ("cart", _("Carrito")),
    ]

    # Estados de respuesta de Transbank
    TRANSBANK_STATUS = [
        ("AUTHORIZED", _("Autorizada")),
        ("FAILED", _("Fallida")),
        ("REJECTED", _("Rechazada")),
        ("CANCELLED", _("Cancelada")),
        ("NULLIFIED", _("Anulada")),
        ("TIMEOUT", _("Tiempo Agotado")),
        ("ABORTED", _("Abortada por Usuario")),
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

    # Nuevos campos para mejor manejo de estados de Transbank
    transbank_status = models.CharField(
        _("estado Transbank"), max_length=20, choices=TRANSBANK_STATUS, null=True, blank=True
    )
    response_code = models.CharField(
        _("código de respuesta"), max_length=10, null=True, blank=True
    )
    authorization_code = models.CharField(
        _("código de autorización"), max_length=50, null=True, blank=True
    )
    error_message = models.TextField(
        _("mensaje de error"), null=True, blank=True
    )
    buy_order = models.CharField(
        _("orden de compra"), max_length=100, null=True, blank=True
    )
    session_id = models.CharField(
        _("ID de sesión"), max_length=100, null=True, blank=True
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
