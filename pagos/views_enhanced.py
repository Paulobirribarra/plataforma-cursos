"""
Vistas mejoradas para el manejo completo de estados de pago con Transbank
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.http import JsonResponse
from .models import Payment
from carrito.models import Cart, CartItem
from .webpay_config import confirmar_transaccion
import logging

logger = logging.getLogger(__name__)


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
        payment.response_code = str(resp.get("response_code", ""))
        payment.authorization_code = resp.get("authorization_code", "")
        
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
        payment.status = "cancelled"
        payment.transbank_status = "ABORTED"
        payment.error_message = "Pago cancelado por el usuario"
        payment.save()
        
        logger.info(f"Pago {payment.id} cancelado por el usuario")
        
        messages.warning(request, "Has cancelado el pago. Puedes intentar nuevamente cuando desees.")
        return render(request, "pagos/payment_cancelled.html", {
            'payment': payment,
            'error_type': 'cancelled'
        })
        
    except Exception as e:
        logger.error(f"Error al procesar transacción abortada {tbk_token}: {e}", exc_info=True)
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
    return render(request, "pagos/payment_timeout.html", {
        'payment': payment,
        'error_type': 'timeout'
    })


def _process_successful_payment(request, payment):
    """Procesa un pago exitoso - reutiliza lógica existente."""
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


@login_required
def payment_status(request, payment_id):
    """Vista para consultar el estado detallado de un pago."""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    return render(request, "pagos/payment_status.html", {
        'payment': payment
    })


@login_required
def check_payment_status(request, payment_id):
    """API endpoint para verificar el estado actual de un pago via AJAX."""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    # Si el pago está pendiente y tiene token, verificar estado en Transbank
    if payment.status == "pending" and payment.transaction_id:
        try:
            from .webpay_config import confirmar_transaccion
            resp = confirmar_transaccion(payment.transaction_id)
            
            # Actualizar estado según respuesta
            if resp.get("status") == "AUTHORIZED" and resp.get("response_code") == 0:
                payment.status = "completed"
                payment.transbank_status = "AUTHORIZED"
                payment.response_code = str(resp.get("response_code", ""))
                payment.authorization_code = resp.get("authorization_code", "")
                payment.save()
                
                # Procesar pago exitoso si aún no se ha procesado
                if payment.payment_type == "cart":
                    _process_successful_payment(request, payment)
                    
            elif resp.get("status") == "REJECTED":
                payment.status = "rejected"
                payment.transbank_status = "REJECTED"
                payment.response_code = str(resp.get("response_code", ""))
                payment.save()
                
        except Exception as e:
            logger.error(f"Error al verificar estado del pago {payment_id}: {e}")
    
    return JsonResponse({
        'status': payment.status,
        'transbank_status': payment.transbank_status,
        'display_status': payment.get_status_display(),
        'updated_at': payment.updated_at.isoformat() if payment.updated_at else None
    })


@login_required
def payment_status_check(request, payment_id):
    """Vista para consultar el estado actual de un pago específico."""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    # Si el pago tiene un token, consultar el estado en Transbank
    if payment.transaction_id and payment.status in ['pending', 'error']:
        try:
            from transbank.webpay.webpay_plus.transaction import Transaction
            from .webpay_config import get_webpay_options
            
            options = get_webpay_options()
            tx = Transaction(options)
            resp = tx.status(payment.transaction_id)
            
            # Actualizar el estado basado en la respuesta
            payment.transbank_status = resp.get("status")
            payment.response_code = str(resp.get("response_code", ""))
            payment.authorization_code = resp.get("authorization_code", "")
            
            if resp.get("status") == "AUTHORIZED" and resp.get("response_code") == 0:
                payment.status = "completed"
            elif resp.get("status") == "REJECTED":
                payment.status = "rejected"
            elif resp.get("status") == "FAILED":
                payment.status = "failed"
                
            payment.save()
            logger.info(f"Estado de pago {payment.id} actualizado a {payment.status}")
            
        except Exception as e:
            logger.error(f"Error al consultar estado de pago {payment.id}: {e}")
            messages.warning(request, "No se pudo consultar el estado actualizado del pago.")
    
    return render(request, "pagos/payment_status.html", {
        'payment': payment
    })


@login_required
def retry_payment(request, payment_id):
    """Vista para reintentar un pago fallido o cancelado."""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    # Solo permitir reintentos en ciertos estados
    if payment.status not in ['failed', 'rejected', 'cancelled', 'timeout', 'error']:
        messages.error(request, "Este pago no puede ser reintentado.")
        return redirect("usuarios:dashboard")
    
    # Crear un nuevo pago con los mismos datos
    new_payment = Payment.objects.create(
        user=payment.user,
        amount=payment.amount,
        description=f"Reintento - {payment.description}",
        status="pending",
        payment_type=payment.payment_type,
        content_type=payment.content_type,
        object_id=payment.object_id
    )
    
    # Redirigir al proceso de pago
    return redirect("pagos:initiate_cart_payment")
