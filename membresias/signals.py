# membresias/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Membership, MembershipHistory


@receiver(post_save, sender=Membership)
def create_membership_history(sender, instance, created, **kwargs):
    """Crea un registro en el historial cuando se crea o actualiza una membresía."""
    if created:
        action = "created"
    else:
        # Determinar la acción basada en los cambios
        if instance.status == "cancelled":
            action = "cancelled"
        elif instance.status == "expired":
            action = "expired"
        else:
            return  # No registrar otros cambios

    MembershipHistory.objects.create(
        membership=instance,
        action=action,
        details={
            "status": instance.status,
            "courses_remaining": instance.courses_remaining,
            "consultations_remaining": instance.consultations_remaining,
        },
    )


@receiver(pre_save, sender=Membership)
def check_membership_expiration(sender, instance, **kwargs):
    """Verifica si la membresía ha expirado y actualiza su estado."""
    if instance.end_date and instance.end_date < timezone.now():
        instance.status = "expired"
