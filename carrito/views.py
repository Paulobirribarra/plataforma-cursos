from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from cursos.models import Course
from membresias.models import MembershipPlan
from .models import Cart, CartItem


def get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(user=user, is_active=True)
    return cart


@login_required
def cart_detail(request):
    cart = get_or_create_cart(request.user)
    applied_discount_code = cart.get_applied_discount_code()
    
    # Calcular precios originales y descuentos
    special_discounts = []
    original_price_total = 0
    
    for item in cart.items.all():
        if item.item_type == 'course':
            # Usar el precio base original
            original_price = item.course.base_price
            original_price_total += original_price
            
            if hasattr(item.course, 'special_discount_percentage') and item.course.special_discount_percentage > 0:
                discount_value = (original_price * item.course.special_discount_percentage) / 100
                special_discounts.append({
                    'course': item.course,
                    'percentage': item.course.special_discount_percentage,
                    'amount': discount_value,
                    'description': f'({item.course.special_discount_percentage}%)'
                })
        elif item.item_type == 'membership':
            original_price = item.membership_plan.price
            original_price_total += original_price    # Calcular el total de descuentos especiales
    total_special_discount = sum(discount['amount'] for discount in special_discounts)
    
    # Calcular el total de todos los descuentos (especiales + cupón)
    total_all_discounts = total_special_discount
    if cart.discount_amount:
        total_all_discounts += cart.discount_amount
    
    context = {
        "cart": cart,
        "subtotal": cart.get_subtotal(),
        "total": cart.get_total(),
        "discount_amount": cart.discount_amount,
        "applied_discount_code": applied_discount_code,
        "special_discounts": special_discounts,
        "total_special_discount": total_special_discount,
        "total_all_discounts": total_all_discounts,
        "original_price_total": original_price_total,
    }
    return render(request, "carrito/cart_detail.html", context)


@login_required
def apply_discount_code(request):
    """Vista para aplicar códigos de descuento"""
    if request.method == "POST":
        cart = get_or_create_cart(request.user)
        code = request.POST.get("discount_code", "").strip()

        if not code:
            messages.error(request, "Por favor, ingresa un código de descuento.")
            return redirect("carrito:cart_detail")        # Remover descuento anterior si existe
        if cart.applied_discount_code_id:
            cart.remove_discount()

        # Aplicar nuevo descuento
        success, message = cart.apply_discount_code(code)

        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)

    return redirect("carrito:cart_detail")


@login_required
def remove_discount_code(request):
    """Vista para remover códigos de descuento"""
    cart = get_or_create_cart(request.user)
    if cart.applied_discount_code_id:
        cart.remove_discount()
        messages.success(request, "Código de descuento removido.")

    return redirect("carrito:cart_detail")


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
