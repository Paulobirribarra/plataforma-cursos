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
    
    # Obtener cursos de recompensa disponibles
    available_courses = membership.get_available_reward_courses()
    
    context = {
        "membership": membership,
        "available_courses": available_courses,
        "title": _("Reclama tus Cursos de Bienvenida"),
        "can_claim": membership.can_claim_reward_course(),
        "courses_remaining": membership.welcome_courses_remaining,
    }
    
    return render(request, "membresias/welcome_courses.html", context)


@login_required
@require_POST
def claim_reward_course(request, course_id):
    """Vista para reclamar un curso de recompensa."""
    course = get_object_or_404(Course, id=course_id)
    
    # Obtener la membresía activa del usuario
    membership = Membership.objects.filter(
        user=request.user, status="active"
    ).first()
    
    if not membership:
        return JsonResponse({
            "success": False,
            "message": _("No tienes una membresía activa.")
        })
    
    # Intentar reclamar el curso
    success, message = membership.claim_reward_course(course)
    
    if success:
        # Crear registro de acceso al curso para el usuario
        from cursos.models import UserCourse
        user_course, created = UserCourse.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={
                'access_start': timezone.now(),
                'progress': 0.0,
                'completed': False
            }
        )
        
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