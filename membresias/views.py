# membresias/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import MembershipPlan, Membership
from cursos.models import Course
from pagos.utils import create_payment


def plan_list(request):
    """Vista para mostrar la lista de planes disponibles."""
    plans = MembershipPlan.objects.filter(is_active=True)
    context = {
        "plans": plans,
        "title": _("Planes de Membresía"),
    }
    return render(request, "membresias/plan_list.html", context)


@login_required
def plan_detail(request, slug):
    """Vista para mostrar los detalles de un plan específico."""
    plan = get_object_or_404(MembershipPlan, slug=slug, is_active=True)
    user_membership = Membership.objects.filter(
        user=request.user, status="active"
    ).first()

    context = {
        "plan": plan,
        "user_membership": user_membership,
        "title": plan.name,
    }
    return render(request, "membresias/plan_detail.html", context)


@login_required
def purchase_membership(request, plan_id):
    """Vista para procesar la compra de una membresía."""
    plan = get_object_or_404(MembershipPlan, id=plan_id, is_active=True)

    # Verificar si el usuario ya tiene una membresía activa
    active_membership = Membership.objects.filter(
        user=request.user, status="active"
    ).first()

    if active_membership:
        messages.warning(
            request,
            _(
                "Ya tienes una membresía activa. Debes cancelarla antes de adquirir una nueva."
            ),
        )
        return redirect("membresias:plan_detail", slug=plan.slug)

    # Crear el pago
    payment = create_payment(
        user=request.user,
        amount=plan.price,
        description=f"Membresía {plan.name}",
        payment_type="membership",
        related_object=plan,
    )

    # Redirigir al proceso de pago
    return redirect("pagos:process_payment", payment_id=payment.id)


@login_required
def my_membership(request):
    """Vista para mostrar la membresía actual del usuario."""
    membership = (
        Membership.objects.filter(user=request.user).order_by("-created_at").first()
    )

    context = {
        "membership": membership,
        "title": _("Mi Membresía"),
    }
    return render(request, "membresias/my_membership.html", context)


@login_required
def cancel_membership(request, membership_id):
    """Vista para cancelar una membresía."""
    membership = get_object_or_404(
        Membership, id=membership_id, user=request.user, status="active"
    )

    if request.method == "POST":
        membership.status = "cancelled"
        membership.auto_renew = False
        membership.save()

        messages.success(request, _("Tu membresía ha sido cancelada exitosamente."))
        return redirect("membresias:my_membership")

    context = {
        "membership": membership,
        "title": _("Cancelar Membresía"),
    }
    return render(request, "membresias/cancel_membership.html", context)


@login_required
def welcome_courses(request):
    """Vista para mostrar los cursos de bienvenida disponibles para reclamar."""
    # Obtener la membresía activa del usuario
    membership = Membership.objects.filter(
        user=request.user, status="active"
    ).first()
    
    if not membership:
        messages.error(request, _("No tienes una membresía activa."))
        return redirect("membresias:plan_list")
    
    # Para plan Premium, redirigir directamente al dashboard (no necesita reclamar)
    if membership.plan.slug == 'premium':
        messages.info(request, _("Como usuario Premium, tienes acceso completo a todos los cursos."))
        return redirect("usuarios:dashboard")
    
    # Obtener cursos de recompensa disponibles y reclamados
    available_courses = membership.get_available_reward_courses()
    claimed_courses = membership.welcome_courses_claimed.all()
    can_claim_general = membership.can_claim_reward_course()
    
    # Preparar información para el template
    courses_with_claim_info = []
    
    if can_claim_general:
        # Mostrar cursos disponibles para reclamar
        for course in available_courses:
            course_info = {
                'course': course,
                'can_claim': True
            }
            courses_with_claim_info.append(course_info)
        
        courses_to_display = available_courses
        show_claimed_only = False
        page_title = _("Reclama tus Cursos de Bienvenida")
    else:
        # Ya no puede reclamar más, mostrar solo los reclamados con mensaje de éxito
        for course in claimed_courses:
            course_info = {
                'course': course,
                'can_claim': False,
                'is_claimed': True
            }
            courses_with_claim_info.append(course_info)
        
        courses_to_display = claimed_courses
        show_claimed_only = True
        page_title = _("¡Felicitaciones! Has Reclamado tus Cursos")
    
    context = {
        "membership": membership,
        "available_courses": available_courses,
        "courses_to_display": courses_to_display,
        "courses_with_claim_info": courses_with_claim_info,
        "claimed_courses": claimed_courses,
        "show_claimed_only": show_claimed_only,
        "can_claim_general": can_claim_general,
        "title": page_title,
        "courses_remaining": membership.welcome_courses_remaining,
    }
    
    return render(request, "membresias/welcome_courses.html", context)


@login_required
@require_POST
def claim_reward_course(request, course_id):
    """Vista para reclamar un curso de recompensa."""
    from django.db import transaction
    
    with transaction.atomic():
        course = get_object_or_404(Course, id=course_id)
        
        # Obtener la membresía activa del usuario con lock
        membership = Membership.objects.select_for_update().filter(
            user=request.user, status="active"
        ).first()
        
        if not membership:
            return JsonResponse({
                "success": False,
                "message": _("No tienes una membresía activa.")
            })
        
        # VALIDACIÓN CRÍTICA: Verificar si ya tiene un UserCourse para este curso
        from cursos.models import UserCourse
        if UserCourse.objects.filter(user=request.user, course=course).exists():
            return JsonResponse({
                "success": False,
                "message": _("Ya tienes acceso a este curso.")
            })
        
        # VALIDACIONES ADICIONALES ANTES DE RECLAMAR
        # 1. Verificar que aún puede reclamar cursos
        if membership.welcome_courses_remaining <= 0:
            return JsonResponse({
                "success": False,
                "message": _("Ya has reclamado todos tus cursos de recompensa disponibles.")
            })
        
        # 2. Verificar que el curso no fue reclamado anteriormente
        if membership.welcome_courses_claimed.filter(id=course.id).exists():
            return JsonResponse({
                "success": False,
                "message": _("Ya has reclamado este curso anteriormente.")
            })
        
        # 3. Verificar que el curso está disponible para su plan
        available_courses = membership.get_available_reward_courses()
        if course not in available_courses:
            return JsonResponse({
                "success": False,
                "message": _("Este curso no está disponible para tu plan.")
            })
        
        # 4. Verificar que es un curso de recompensa
        if not course.is_membership_reward:
            return JsonResponse({
                "success": False,
                "message": _("Este curso no es una recompensa.")
            })
        
        # 5. Verificar que el plan del usuario puede reclamar este curso
        if not course.reward_for_plans.filter(id=membership.plan.id).exists():
            return JsonResponse({
                "success": False,
                "message": _("Tu plan no puede reclamar este curso.")
            })
        
        # Intentar reclamar el curso (con todas las validaciones internas)
        success, message = membership.claim_reward_course(course)
        
        if success:
            # Crear registro de acceso al curso para el usuario SOLO si no existe
            user_course, created = UserCourse.objects.get_or_create(
                user=request.user,
                course=course,
                defaults={
                    'access_start': timezone.now(),
                    'progress': 0.0,
                    'completed': False
                }
            )
            
            if not created:
                # Si ya existía el UserCourse, esto es un error - debemos revertir el reclamo
                # Esto no debería pasar, pero es una medida de seguridad
                membership.welcome_courses_claimed.remove(course)
                membership.welcome_courses_remaining += 1
                membership.save()
                
                return JsonResponse({
                    "success": False,
                    "message": _("Error: Ya tienes acceso a este curso.")
                })
            
            # Recargar membership para obtener los datos actualizados
            membership.refresh_from_db()
            
            return JsonResponse({
                "success": True,
                "message": message,
                "courses_remaining": membership.welcome_courses_remaining,
                "redirect_url": "/usuarios/dashboard/" if membership.welcome_courses_remaining == 0 else None
            })
        else:
            return JsonResponse({
                "success": False,
                "message": message
            })


@login_required
def skip_welcome_courses(request):
    """Vista para saltar la selección de cursos de bienvenida."""
    membership = Membership.objects.filter(
        user=request.user, status="active"
    ).first()
    
    if membership:
        messages.info(request, _(
            "Puedes reclamar tus cursos de bienvenida más tarde desde tu dashboard. "
            "Tienes {} curso(s) disponible(s) para reclamar."
        ).format(membership.welcome_courses_remaining))
    
    return redirect("usuarios:dashboard")


@login_required
def welcome_courses_debug(request):
    """Vista de debug para probar botones sin problemas de CSS."""
    # Obtener la membresía activa del usuario
    membership = Membership.objects.filter(
        user=request.user, status="active"
    ).first()
    
    if not membership:
        messages.error(request, _("No tienes una membresía activa."))
        return redirect("membresias:plan_list")
    
    # Para plan Premium, redirigir directamente al dashboard (no necesita reclamar)
    if membership.plan.slug == 'premium':
        messages.info(request, _("Como usuario Premium, tienes acceso completo a todos los cursos."))
        return redirect("usuarios:dashboard")
        # Obtener cursos de recompensa disponibles
    available_courses = membership.get_available_reward_courses()
    claimed_courses = membership.welcome_courses_claimed.all()
    
    # Agregar información de disponibilidad a cada curso
    courses_with_claim_info = []
    can_claim_general = membership.can_claim_reward_course()
    
    # Si el usuario puede reclamar, mostrar cursos disponibles
    # Si ya no puede reclamar, mostrar solo los reclamados
    if can_claim_general:
        for course in available_courses:
            course_info = {
                'course': course,
                'can_claim': True
            }
            courses_with_claim_info.append(course_info)
        
        courses_to_display = available_courses
        show_claimed_only = False
    else:
        # Ya no puede reclamar más, mostrar solo los reclamados
        for course in claimed_courses:
            course_info = {
                'course': course,
                'can_claim': False,
                'is_claimed': True
            }
            courses_with_claim_info.append(course_info)
        
        courses_to_display = claimed_courses
        show_claimed_only = True
    
    context = {
        "membership": membership,
        "available_courses": available_courses,
        "courses_with_claim_info": courses_with_claim_info,
        "title": _("DEBUG: Reclama tus Cursos de Bienvenida"),
        "can_claim": can_claim_general,
        "courses_remaining": membership.welcome_courses_remaining,
    }
    
    return render(request, "membresias/welcome_courses_debug.html", context)