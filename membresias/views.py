# membresias/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import MembershipPlan, Membership
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

    return redirect("membresias:my_membership")
