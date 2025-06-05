from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType
from transbank.common.options import WebpayOptions
from decouple import config
import logging

logger = logging.getLogger(__name__)

# Configuración del ambiente según variables de entorno
environment = config('WEBPAY_ENVIRONMENT', default='INTEGRATION')

def get_webpay_options():
    """Obtiene las opciones de configuración para Webpay"""
    if environment == 'INTEGRATION':
        # Para ambiente de integración usar credenciales predeterminadas
        return WebpayOptions(
            commerce_code='597055555532',
            api_key='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C',
            integration_type=IntegrationType.TEST
        )
    else:
        # Para producción usar credenciales del .env
        commerce_code = config('WEBPAY_COMMERCE_CODE')
        api_key = config('WEBPAY_API_KEY')
        return WebpayOptions(
            commerce_code=commerce_code,
            api_key=api_key,
            integration_type=IntegrationType.LIVE
        )

def configure_webpay():
    """Configura Webpay según el ambiente especificado"""
    try:
        options = get_webpay_options()
        logger.info(f"Webpay configurado para ambiente: {environment}")
        logger.info(f"Commerce Code: {options.commerce_code}")
        return True
    except Exception as e:
        logger.error(f"Error configurando Webpay: {e}")
        return False

# Configurar automáticamente al importar el módulo
configure_webpay()

def crear_transaccion(buy_order, session_id, amount, return_url):
    """Crea una transacción usando el SDK oficial de Transbank"""
    try:
        options = get_webpay_options()
        tx = Transaction(options)
        
        response = tx.create(
            buy_order=buy_order,
            session_id=session_id,
            amount=int(amount),
            return_url=return_url
        )
        logger.info(f"Transacción creada exitosamente: {buy_order}")
        return response
    except Exception as e:
        logger.error(f"Error creando transacción: {e}")
        raise

def confirmar_transaccion(token):
    """Confirma una transacción usando el SDK oficial de Transbank"""
    try:
        options = get_webpay_options()
        tx = Transaction(options)
        
        response = tx.commit(token)
        logger.info(f"Transacción confirmada exitosamente: {token}")
        return response
    except Exception as e:
        logger.error(f"Error confirmando transacción: {e}")
        raise
