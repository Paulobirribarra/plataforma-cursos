from django.urls import path
from . import views
from . import views_enhanced

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
    # URLs originales (mantener por compatibilidad)
    path("webpay/return/", views.webpay_return, name="webpay_return"),
    path("webpay/final/", views.webpay_final, name="webpay_final"),
      # Nuevas URLs mejoradas
    path("webpay/return-enhanced/", views_enhanced.webpay_return_enhanced, name="webpay_return_enhanced"),
    path("payment-status/<int:payment_id>/", views_enhanced.payment_status, name="payment_status"),
    path("check-payment-status/<int:payment_id>/", views_enhanced.check_payment_status, name="check_payment_status"),
    path("retry-payment/<int:payment_id>/", views_enhanced.retry_payment, name="retry_payment"),
    
    path("exito/", views.purchase_success, name="purchase_success"),
]
