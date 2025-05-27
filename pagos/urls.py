from django.urls import path
from . import views

app_name = "pagos"

urlpatterns = [
    path("procesar/<int:payment_id>/", views.process_payment, name="process_payment"),
    path("confirmar/<int:payment_id>/", views.confirm_payment, name="confirm_payment"),
    path("cancelar/<int:payment_id>/", views.cancel_payment, name="cancel_payment"),
    path("carrito/pagar/", views.initiate_cart_payment, name="initiate_cart_payment"),
    path(
        "carrito/confirmar/<int:payment_id>/",
        views.confirm_cart_payment,
        name="confirm_cart_payment",
    ),
    path("webpay/return/", views.webpay_return, name="webpay_return"),
    path("webpay/final/", views.webpay_final, name="webpay_final"),
    path("exito/", views.purchase_success, name="purchase_success"),
]
