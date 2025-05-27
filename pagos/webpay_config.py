from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.webpay.webpay_plus import WebpayPlus

# Configuración para ambiente de pruebas
WebpayPlus.configure_for_testing()

# Configuración para producción (descomentar y configurar cuando esté listo)
# WebpayPlus.configure(
#     commerce_code="TU_CODIGO_COMERCIO",
#     api_key="TU_API_KEY",
#     environment="PRODUCTION"
# )
