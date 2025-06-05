from django.urls import path
from . import views

app_name = "carrito"

urlpatterns = [
    path("", views.cart_detail, name="cart_detail"),
    path(
        "agregar/curso/<int:course_id>/",
        views.add_course_to_cart,
        name="add_course_to_cart",
    ),
    path(
        "agregar/membresia/<int:plan_id>/",
        views.add_membership_to_cart,
        name="add_membership_to_cart",
    ),
    path(
        "eliminar/item/<int:item_id>/",
        views.remove_item_from_cart,
        name="remove_item_from_cart",
    ),
    path("vaciar/", views.clear_cart, name="clear_cart"),
    path("aplicar-descuento/", views.apply_discount_code, name="apply_discount_code"),
    path("remover-descuento/", views.remove_discount_code, name="remove_discount_code"),
]
