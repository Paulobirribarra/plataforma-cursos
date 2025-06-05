from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from .models import Payment
from carrito.models import Cart, CartItem
from membresias.models import MembershipPlan
from .webpay_config import crear_transaccion, confirmar_transaccion
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
    
    if payment.status == "pending":
        payment.status = "cancelled"
        payment.save()
        messages.info(request, "Pago cancelado.")
    else:
        messages.error(request, "Este pago no puede ser cancelado.")
    
    return redirect("carrito:cart_detail")


@login_required
def initiate_cart_payment(request):
    cart = Cart.objects.filter(user=request.user, is_active=True).first()
    if not cart or not cart.items.exists():
        messages.error(request, "Tu carrito está vacío.")
        return redirect("carrito:cart_detail")    # Calcular el total
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

    # Si el total es 0, procesar como pago gratuito
    if total == 0:
        logger.info(f"Procesando pago gratuito para pago {payment.id}")
        return process_free_payment(request, payment)

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
            purchased_items = []
            has_new_membership = False
            has_new_courses = False
            
            if cart:
                # Guardar items para mostrar en confirmación
                purchased_items = list(cart.items.all())
                
                for item in cart.items.all():
                    if item.item_type == "course" and item.course:
                        from cursos.models import UserCourse
                        UserCourse.objects.get_or_create(
                            user=request.user, 
                            course=item.course,
                            defaults={'progress': 0.0, 'completed': False}
                        )
                        has_new_courses = True
                    elif item.item_type == "membership" and item.membership_plan:
                        from membresias.models import Membership
                        # Verificar si ya existe una membresía activa
                        existing_membership = Membership.objects.filter(
                            user=request.user, 
                            status='active'
                        ).first()
                        
                        if existing_membership:
                            # Actualizar membresía existente
                            existing_membership.plan = item.membership_plan
                            existing_membership.courses_remaining = item.membership_plan.courses_per_month
                            existing_membership.consultations_remaining = item.membership_plan.consultations
                            existing_membership.save()
                        else:
                            # Crear nueva membresía
                            Membership.objects.create(
                                user=request.user,
                                plan=item.membership_plan,
                                status="active",
                                courses_remaining=item.membership_plan.courses_per_month,
                                consultations_remaining=item.membership_plan.consultations
                            )
                        has_new_membership = True
                
                cart.is_active = False
                cart.save()
            
            # Guardar información en sesión para la página de confirmación
            request.session['purchase_success_data'] = {
                'payment_id': payment.id,
                'purchased_items': [
                    {
                        'item_type': item.item_type,
                        'course_title': item.course.title if item.course else None,
                        'membership_name': item.membership_plan.name if item.membership_plan else None,
                        'price_applied': float(item.price_applied)
                    } for item in purchased_items
                ],
                'has_new_membership': has_new_membership,
                'has_new_courses': has_new_courses,
                'total_amount': float(payment.amount)
            }
            
            return redirect("pagos:purchase_success")
        else:
            payment.status = "failed"
            payment.save()
            messages.error(request, "El pago no pudo ser procesado.")
            return redirect("carrito:cart_detail")
    except Exception as e:
        logger.error(f"Error al confirmar el pago: {e}", exc_info=True)
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
            purchased_items = []
            has_new_membership = False
            has_new_courses = False
            
            if cart:
                # Guardar items para mostrar en confirmación
                purchased_items = list(cart.items.all())
                
                for item in cart.items.all():
                    if item.item_type == "course" and item.course:
                        from cursos.models import UserCourse
                        UserCourse.objects.get_or_create(
                            user=request.user, 
                            course=item.course,
                            defaults={'progress': 0.0, 'completed': False}
                        )
                        has_new_courses = True
                    elif item.item_type == "membership" and item.membership_plan:
                        from membresias.models import Membership
                        # Verificar si ya existe una membresía activa
                        existing_membership = Membership.objects.filter(
                            user=request.user, 
                            status='active'
                        ).first()
                        
                        if existing_membership:
                            # Actualizar membresía existente
                            existing_membership.plan = item.membership_plan
                            existing_membership.courses_remaining = item.membership_plan.courses_per_month
                            existing_membership.consultations_remaining = item.membership_plan.consultations
                            existing_membership.save()
                        else:
                            # Crear nueva membresía
                            Membership.objects.create(
                                user=request.user,
                                plan=item.membership_plan,
                                status="active",
                                courses_remaining=item.membership_plan.courses_per_month,
                                consultations_remaining=item.membership_plan.consultations
                            )
                        has_new_membership = True
                
                cart.is_active = False
                cart.save()

            # Guardar información en sesión para la página de confirmación
            request.session['purchase_success_data'] = {
                'payment_id': payment.id,
                'purchased_items': [
                    {
                        'item_type': item.item_type,
                        'course_title': item.course.title if item.course else None,
                        'membership_name': item.membership_plan.name if item.membership_plan else None,
                        'price_applied': float(item.price_applied)
                    } for item in purchased_items
                ],
                'has_new_membership': has_new_membership,
                'has_new_courses': has_new_courses,
                'total_amount': float(payment.amount)
            }
            
            return redirect("pagos:purchase_success")
        else:
            payment.status = "failed"
            payment.save()
            messages.error(request, "El pago fue rechazado.")

    except Exception as e:
        logger.error(f"Error al confirmar el pago: {e}", exc_info=True)
        payment.status = "failed"
        payment.save()
        messages.error(request, f"Error al confirmar el pago: {str(e)}")

    return redirect("carrito:cart_detail")


@login_required
def webpay_final(request):
    """Vista final después del pago."""
    return redirect("usuarios:dashboard")


@login_required
def purchase_success(request):
    """Vista para mostrar la confirmación de compra exitosa."""
    # Obtener datos de la sesión
    success_data = request.session.get('purchase_success_data')
    
    if not success_data:
        messages.warning(request, "No se encontró información de compra reciente.")
        return redirect("usuarios:dashboard")
    
    # Limpiar la sesión después de obtener los datos
    del request.session['purchase_success_data']
    
    # Obtener el pago
    payment = get_object_or_404(Payment, id=success_data['payment_id'], user=request.user)
    
    # Si se compró una membresía, redirigir a la selección de cursos de bienvenida
    if success_data['has_new_membership']:
        # Verificar si el usuario tiene una membresía que requiere selección de cursos
        from membresias.models import Membership
        membership = Membership.objects.filter(user=request.user, status='active').first()
        
        if membership and membership.plan.slug != 'premium' and membership.welcome_courses_remaining > 0:
            messages.success(request, f"¡Felicitaciones! Tu membresía {membership.plan.name} ha sido activada. Ahora puedes elegir tus cursos de bienvenida.")
            return redirect("membresias:welcome_courses")
        else:
            # Para Premium o si no hay cursos de bienvenida, ir al dashboard
            messages.success(request, "¡Compra exitosa! Tu membresía ha sido activada.")
            return redirect("usuarios:dashboard")
    
    # Para compras de cursos individuales, mostrar página de confirmación normal
    context = {
        'payment': payment,
        'purchased_items': success_data['purchased_items'],
        'has_new_membership': success_data['has_new_membership'],
        'has_new_courses': success_data['has_new_courses'],
        'total_amount': success_data['total_amount'],
    }
    
    return render(request, 'pagos/purchase_success.html', context)


def process_free_payment(request, payment):
    """Procesa un pago gratuito (monto = 0) sin pasar por Webpay."""
    try:
        # Marcar el pago como completado
        payment.status = "completed"
        payment.save()
        
        # Procesar los items del carrito igual que en confirm_cart_payment
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
        purchased_items = []
        has_new_membership = False
        has_new_courses = False
        
        if cart:
            # Guardar items para mostrar en confirmación
            purchased_items = list(cart.items.all())
            
            for item in cart.items.all():
                if item.item_type == "course" and item.course:
                    from cursos.models import UserCourse
                    UserCourse.objects.get_or_create(
                        user=request.user, 
                        course=item.course,
                        defaults={'progress': 0.0, 'completed': False}
                    )
                    has_new_courses = True
                elif item.item_type == "membership" and item.membership_plan:
                    from membresias.models import Membership
                    # Verificar si ya existe una membresía activa
                    existing_membership = Membership.objects.filter(
                        user=request.user, 
                        status='active'
                    ).first()
                    
                    if existing_membership:
                        # Actualizar membresía existente
                        existing_membership.plan = item.membership_plan
                        existing_membership.courses_remaining = item.membership_plan.courses_per_month
                        existing_membership.consultations_remaining = item.membership_plan.consultations
                        existing_membership.save()
                    else:
                        # Crear nueva membresía
                        Membership.objects.create(
                            user=request.user,
                            plan=item.membership_plan,
                            status="active",
                            courses_remaining=item.membership_plan.courses_per_month,
                            consultations_remaining=item.membership_plan.consultations
                        )
                    has_new_membership = True
            
            cart.is_active = False
            cart.save()

        # Guardar información en sesión para la página de confirmación
        request.session['purchase_success_data'] = {
            'payment_id': payment.id,
            'purchased_items': [
                {
                    'item_type': item.item_type,
                    'course_title': item.course.title if item.course else None,
                    'membership_name': item.membership_plan.name if item.membership_plan else None,
                    'price_applied': float(item.price_applied)
                } for item in purchased_items
            ],
            'has_new_membership': has_new_membership,
            'has_new_courses': has_new_courses,
            'total_amount': float(payment.amount)
        }
        
        logger.info(f"Pago gratuito procesado exitosamente para pago {payment.id}")
        messages.success(request, "¡Curso gratuito agregado exitosamente!")
        return redirect("pagos:purchase_success")
        
    except Exception as e:
        logger.error(f"Error al procesar pago gratuito: {e}", exc_info=True)
        payment.status = "failed"
        payment.save()
        messages.error(request, f"Error al procesar el curso gratuito: {e}")
        return redirect("carrito:cart_detail")
