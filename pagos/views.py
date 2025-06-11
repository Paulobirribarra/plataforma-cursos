from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils import timezone
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

    description += ", ".join(items_desc)    # Crear el pago
    payment = Payment.objects.create(
        amount=total,
        description=description,
        status="pending",
        payment_type="cart",
        user=request.user,
        buy_order=f"ORDER_{request.user.id}_{int(timezone.now().timestamp())}",
        session_id=str(request.user.id),
    )

    # Si el total es 0, procesar como pago gratuito
    if total == 0:
        logger.info(f"Procesando pago gratuito para pago {payment.id}")
        return process_free_payment(request, payment)    # Iniciar transacción con Webpay REST
    return_url = request.build_absolute_uri(
        reverse("pagos:webpay_return_enhanced")
    )
    try:
        logger.info(
            f"Iniciando transacción Webpay para pago {payment.id} (total: {total})"
        )
        resp = crear_transaccion(
            buy_order=payment.buy_order,
            session_id=payment.session_id,
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


@login_required
def webpay_return_enhanced(request):
    """Vista mejorada que maneja TODOS los posibles retornos de Webpay."""
    logger.info(f"Retorno de Webpay recibido: GET={request.GET.dict()}, POST={request.POST.dict()}")
    
    # Determinar el tipo de retorno según los parámetros recibidos
    token_ws = request.GET.get("token_ws") or request.POST.get("token_ws")
    tbk_token = request.GET.get("TBK_TOKEN") or request.POST.get("TBK_TOKEN")
    tbk_orden_compra = request.GET.get("TBK_ORDEN_COMPRA") or request.POST.get("TBK_ORDEN_COMPRA")
    tbk_id_sesion = request.GET.get("TBK_ID_SESION") or request.POST.get("TBK_ID_SESION")
    
    payment = None
    
    try:
        # Caso 1: Flujo normal (éxito o rechazo) - llega token_ws
        if token_ws:
            logger.info(f"Flujo normal detectado con token: {token_ws}")
            payment = get_object_or_404(Payment, transaction_id=token_ws, user=request.user)
            return _handle_normal_flow(request, payment, token_ws)
        
        # Caso 2: Pago abortado por usuario - llega TBK_TOKEN
        elif tbk_token:
            logger.info(f"Pago abortado detectado con TBK_TOKEN: {tbk_token}")
            payment = get_object_or_404(Payment, transaction_id=tbk_token, user=request.user)
            return _handle_aborted_payment(request, payment, tbk_token)
        
        # Caso 3: Timeout - llegan TBK_ORDEN_COMPRA y TBK_ID_SESION sin token
        elif tbk_orden_compra and tbk_id_sesion:
            logger.info(f"Timeout detectado - Orden: {tbk_orden_compra}, Sesión: {tbk_id_sesion}")
            payment = get_object_or_404(Payment, buy_order=tbk_orden_compra, session_id=tbk_id_sesion, user=request.user)
            return _handle_timeout(request, payment)
        
        # Caso 4: Error desconocido
        else:
            logger.error("Retorno de Webpay sin parámetros reconocibles")
            messages.error(request, "Error en el proceso de pago. No se recibieron parámetros válidos.")
            return redirect("carrito:cart_detail")
            
    except Payment.DoesNotExist:
        logger.error(f"Pago no encontrado para usuario {request.user.id}")
        messages.error(request, "No se encontró la transacción solicitada.")
        return redirect("carrito:cart_detail")
    except Exception as e:
        logger.error(f"Error inesperado en webpay_return_enhanced: {e}", exc_info=True)
        if payment:
            payment.status = "error"
            payment.error_message = str(e)
            payment.save()
        messages.error(request, "Error inesperado en el proceso de pago.")
        return redirect("carrito:cart_detail")


def _handle_normal_flow(request, payment, token):
    """Maneja el flujo normal donde el usuario completó o fue rechazado el pago."""
    try:
        resp = confirmar_transaccion(token)
        logger.info(f"Respuesta de confirmación: {resp}")
        
        # Actualizar campos de respuesta de Transbank
        payment.transbank_status = resp.get("status")
        payment.response_code = resp.get("response_code")
        payment.authorization_code = resp.get("authorization_code")
        
        if resp.get("status") == "AUTHORIZED" and resp.get("response_code") == 0:
            payment.status = "completed"
            payment.save()
            logger.info(f"Pago {payment.id} autorizado exitosamente")
            return _process_successful_payment(request, payment)
        
        elif resp.get("status") == "REJECTED":
            payment.status = "rejected"
            payment.transbank_status = "REJECTED"
            payment.error_message = "Transacción rechazada por el banco emisor"
            payment.save()
            logger.info(f"Pago {payment.id} rechazado por el banco")
            return _handle_rejected_payment(request, payment)
        
        elif resp.get("status") == "FAILED":
            payment.status = "failed"
            payment.transbank_status = "FAILED"
            payment.error_message = "Transacción fallida durante el procesamiento"
            payment.save()
            logger.info(f"Pago {payment.id} falló durante el procesamiento")
            return _handle_failed_payment(request, payment)
        
        else:
            # Estado desconocido
            payment.status = "error"  
            payment.error_message = f"Estado desconocido: {resp.get('status')}"
            payment.save()
            logger.warning(f"Estado desconocido para pago {payment.id}: {resp.get('status')}")
            return _handle_unknown_status(request, payment, resp)
            
    except Exception as e:
        logger.error(f"Error al confirmar transacción {token}: {e}", exc_info=True)
        payment.status = "error"
        payment.error_message = f"Error al confirmar transacción: {str(e)}"
        payment.save()
        return _handle_transaction_error(request, payment, str(e))


def _handle_aborted_payment(request, payment, tbk_token):
    """Maneja el caso donde el usuario abortó el pago en el formulario de Webpay."""
    try:
        # Consultar estado sin confirmar (usando el método status)
        resp = confirmar_transaccion(tbk_token)  # También podríamos usar status() del SDK
        
        payment.status = "cancelled"
        payment.transbank_status = "ABORTED"
        payment.error_message = "Pago cancelado por el usuario"
        payment.save()
        
        logger.info(f"Pago {payment.id} cancelado por el usuario")
        
        messages.warning(request, "Has cancelado el pago. Puedes intentar nuevamente cuando desees.")
        return redirect("carrito:cart_detail")
        
    except Exception as e:
        logger.error(f"Error al consultar transacción abortada {tbk_token}: {e}", exc_info=True)
        payment.status = "cancelled"
        payment.error_message = "Pago cancelado por el usuario"
        payment.save()
        messages.warning(request, "Has cancelado el pago. Puedes intentar nuevamente cuando desees.")
        return redirect("carrito:cart_detail")


def _handle_timeout(request, payment):
    """Maneja el caso donde se agotó el tiempo en el formulario de Webpay."""
    payment.status = "timeout"
    payment.transbank_status = "TIMEOUT"
    payment.error_message = "Tiempo agotado en el formulario de pago"
    payment.save()
    
    logger.info(f"Timeout para pago {payment.id}")
    
    messages.error(request, "Se agotó el tiempo para completar el pago. Por favor, intenta nuevamente.")
    return redirect("carrito:cart_detail")


def _process_successful_payment(request, payment):
    """Procesa un pago exitoso - lógica existente."""
    # ... aquí va toda la lógica actual de confirm_cart_payment para pagos exitosos
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


def _handle_rejected_payment(request, payment):
    """Maneja un pago rechazado por el banco."""
    messages.error(request, 
        "Tu tarjeta fue rechazada por el banco emisor. "
        "Verifica tus datos o intenta con otra tarjeta."
    )
    return render(request, "pagos/payment_rejected.html", {
        'payment': payment,
        'error_type': 'rejected'
    })


def _handle_failed_payment(request, payment):
    """Maneja un pago que falló durante el procesamiento."""
    messages.error(request, 
        "Ocurrió un error durante el procesamiento del pago. "
        "Por favor, intenta nuevamente."
    )
    return render(request, "pagos/payment_failed.html", {
        'payment': payment,
        'error_type': 'failed'
    })


def _handle_unknown_status(request, payment, response):
    """Maneja estados desconocidos de respuesta."""
    logger.warning(f"Estado desconocido recibido: {response}")
    messages.error(request, 
        "Se recibió una respuesta inesperada del sistema de pagos. "
        "Contacta con soporte si el problema persiste."
    )
    return render(request, "pagos/payment_error.html", {
        'payment': payment,
        'error_type': 'unknown',
        'response': response
    })


def _handle_transaction_error(request, payment, error_message):
    """Maneja errores durante la confirmación de transacción."""
    messages.error(request, 
        "Error al procesar la confirmación del pago. "
        "Contacta con soporte para verificar el estado de tu transacción."
    )
    return render(request, "pagos/payment_error.html", {
        'payment': payment,
        'error_type': 'transaction_error',
        'error_message': error_message
    })

