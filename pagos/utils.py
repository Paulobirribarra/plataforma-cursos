from django.contrib.contenttypes.models import ContentType
from .models import Payment


def create_payment(user, amount, description, payment_type, related_object):
    """Función de utilidad para crear un pago."""
    content_type = ContentType.objects.get_for_model(related_object)

    payment = Payment.objects.create(
        user=user,
        amount=amount,
        description=description,
        payment_type=payment_type,
        content_type=content_type,
        object_id=related_object.id,
    )

    return payment
