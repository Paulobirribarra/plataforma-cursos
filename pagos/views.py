from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from .models import Payment
from carrito.models import Cart, CartItem
from membresias.models import MembershipPlan
from .webpay_rest import crear_transaccion, confirmar_transaccion
import logging

logger = logging.getLogger(__name__)


@login_required
def process_payment(request, payment_id):
    """Vista para procesar un pago."""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    if payment.status != "pending":
        messages.error(request, _("Este pago ya ha sido procesado."))
        return redirect("usuarios:dashboard")

    context = {
        "payment": payment,
        "title": _("Procesar Pago"),
    }
    return render(request, "pagos/process_payment.html", context)


@login_required
def confirm_payment(request, payment_id):
    """Vista para confirmar un pago exitoso."""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    if payment.status != "pending":
        messages.error(request, _("Este pago ya ha sido procesado."))
        return redirect("usuarios:dashboard")

    # Aquí iría la lógica de integración con el sistema de pagos
    payment.status = "completed"
    payment.save()

    # Crear la membresía si el pago es de tipo membership
    if payment.payment_type == "membership":
        from membresias.models import Membership

        plan = payment.content_object
        Membership.objects.create(user=request.user, plan=plan, status="active")

    messages.success(request, _("¡Pago procesado exitosamente!"))
    return redirect("usuarios:dashboard")


@login_required
def cancel_payment(request, payment_id):
    """Vista para cancelar un pago."""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    if payment.status != "pending":
        messages.error(request, _("Este pago ya ha sido procesado."))
        return redirect("usuarios:dashboard")

    payment.status = "cancelled"
    payment.save()

    messages.info(request, _("Pago cancelado."))
    return redirect("usuarios:dashboard")


@login_required
def initiate_cart_payment(request):
    cart = Cart.objects.filter(user=request.user, is_active=True).first()
    if not cart or not cart.items.exists():
        messages.error(request, "Tu carrito está vacío.")
        return redirect("carrito:cart_detail")

    # Calcular el total
    total = sum(item.price_applied for item in cart.items.all())
    description = "Compra de "
    items_desc = []
    for item in cart.items.all():
        if item.item_type == "course" and item.course:
            items_desc.append(f"Curso: {item.course.title}")
        elif item.item_type == "membership" and item.membership_plan:
            items_desc.append(f"Membresía: {item.membership_plan.name}")

    description += ", ".join(items_desc)

    # Crear el pago
    payment = Payment.objects.create(
        amount=total,
        description=description,
        status="pending",
        payment_type="cart",
        user=request.user,
    )

    # Iniciar transacción con Webpay REST
    return_url = request.build_absolute_uri(
        reverse("pagos:confirm_cart_payment", args=[payment.id])
    )
    try:
        logger.info(
            f"Iniciando transacción Webpay para pago {payment.id} (total: {total})"
        )
        resp = crear_transaccion(
            buy_order=str(payment.id),
            session_id=str(request.user.id),
            amount=total,
            return_url=return_url,
        )
        logger.info(f"Respuesta Webpay: {resp}")
        payment.transaction_id = resp["token"]
        payment.save()
        # Redirigir al formulario de Webpay
        return redirect(resp["url"] + "?token_ws=" + resp["token"])
    except Exception as e:
        logger.error(f"Error al iniciar pago Webpay: {e}", exc_info=True)
        payment.status = "failed"
        payment.save()
        messages.error(request, f"Error al iniciar el pago: {e}")
        return redirect("carrito:cart_detail")


@login_required
def confirm_cart_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    token = request.GET.get("token_ws") or payment.transaction_id
    if not token:
        messages.error(request, "Token de pago no recibido.")
        return redirect("carrito:cart_detail")
    try:
        resp = confirmar_transaccion(token)
        if resp.get("status") == "AUTHORIZED":
            payment.status = "completed"
            payment.save()
            # Procesar los items del carrito
            cart = Cart.objects.filter(user=request.user, is_active=True).first()
            if cart:
                for item in cart.items.all():
                    if item.item_type == "course" and item.course:
                        request.user.courses.add(item.course)
                    elif item.item_type == "membership" and item.membership_plan:
                        request.user.membership = item.membership_plan
                        request.user.save()
                cart.is_active = False
                cart.save()
            messages.success(request, "¡Pago completado exitosamente!")
            return redirect("usuarios:profile")
        else:
            payment.status = "failed"
            payment.save()
            messages.error(request, "El pago no pudo ser procesado.")
            return redirect("carrito:cart_detail")
    except Exception as e:
        payment.status = "failed"
        payment.save()
        messages.error(request, f"Error al confirmar el pago: {e}")
        return redirect("carrito:cart_detail")


@login_required
def webpay_return(request):
    """Vista que maneja el retorno de Webpay después del pago."""
    token = request.GET.get("token_ws")
    payment_id = request.session.get("payment_id")

    if not token or not payment_id:
        messages.error(request, "Error en el proceso de pago.")
        return redirect("carrito:cart_detail")

    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    try:
        result = confirmar_transaccion(token)

        if result.get("status") == "AUTHORIZED":
            payment.status = "completed"
            payment.save()

            # Procesar los ítems del carrito
            cart = Cart.objects.filter(user=request.user, is_active=True).first()
            if cart:
                for item in cart.items.all():
                    if item.item_type == "course" and item.course:
                        from cursos.models import UserCourse

                        UserCourse.objects.get_or_create(
                            user=request.user, course=item.course
                        )
                    elif item.item_type == "membership" and item.membership_plan:
                        from membresias.models import Membership

                        Membership.objects.create(
                            user=request.user,
                            plan=item.membership_plan,
                            status="active",
                        )
                cart.is_active = False
                cart.save()

            messages.success(request, "¡Pago procesado exitosamente!")
        else:
            payment.status = "failed"
            payment.save()
            messages.error(request, "El pago fue rechazado.")

    except Exception as e:
        payment.status = "failed"
        payment.save()
        messages.error(request, f"Error al confirmar el pago: {str(e)}")

    return redirect("usuarios:dashboard")


@login_required
def webpay_final(request):
    """Vista final después del pago."""
    return redirect("usuarios:dashboard")
