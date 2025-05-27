from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cursos.models import Course
from membresias.models import MembershipPlan
from .models import Cart, CartItem


def get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(user=user, is_active=True)
    return cart


@login_required
def cart_detail(request):
    cart = get_or_create_cart(request.user)
    return render(request, "carrito/cart_detail.html", {"cart": cart})


@login_required
def add_course_to_cart(request, course_id):
    cart = get_or_create_cart(request.user)
    course = get_object_or_404(Course, pk=course_id)
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        item_type="course",
        course=course,
        defaults={"price_applied": course.get_final_price()},
    )
    if not created:
        messages.info(request, "El curso ya está en tu carrito.")
    else:
        messages.success(request, "Curso agregado al carrito.")
    return redirect("carrito:cart_detail")


@login_required
def add_membership_to_cart(request, plan_id):
    cart = get_or_create_cart(request.user)
    plan = get_object_or_404(MembershipPlan, pk=plan_id)
    # Solo permitir una membresía por carrito
    existing_item = cart.items.filter(item_type="membership").first()
    if existing_item:
        messages.warning(
            request,
            f"Ya tienes la membresía '{existing_item.membership_plan.name}' en tu carrito. Elimina esa membresía para agregar otra.",
        )
    else:
        CartItem.objects.create(
            cart=cart,
            item_type="membership",
            membership_plan=plan,
            price_applied=plan.price,
        )
        messages.success(request, "Membresía agregada al carrito.")
    return redirect("carrito:cart_detail")


@login_required
def remove_item_from_cart(request, item_id):
    cart = get_or_create_cart(request.user)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    item.delete()
    messages.success(request, "Ítem eliminado del carrito.")
    return redirect("carrito:cart_detail")


@login_required
def clear_cart(request):
    cart = get_or_create_cart(request.user)
    cart.items.all().delete()
    messages.success(request, "Carrito vaciado.")
    return redirect("carrito:cart_detail")
