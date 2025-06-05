#!/usr/bin/env python
"""
Script de prueba para verificar la configuración de Webpay usando el SDK oficial
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plataforma_cursos.settings')
django.setup()

from pagos.webpay_config import crear_transaccion, confirmar_transaccion, configure_webpay
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_webpay_configuration():
    """Prueba la configuración de Webpay"""
    print("🔧 Probando configuración de Webpay...")
    
    try:
        # Verificar configuración
        config_result = configure_webpay()
        if config_result:
            print("✅ Webpay configurado correctamente")
        else:
            print("❌ Error en la configuración de Webpay")
            return False
            
        # Crear transacción de prueba
        print("\n💳 Creando transacción de prueba...")
        
        buy_order = "test_order_123"
        session_id = "test_session_456"
        amount = 10000  # $10.000 CLP
        return_url = "http://localhost:8000/pagos/test/return/"
        
        response = crear_transaccion(
            buy_order=buy_order,
            session_id=session_id,
            amount=amount,
            return_url=return_url
        )
        
        print(f"✅ Transacción creada exitosamente:")
        print(f"   Token: {response.get('token', 'N/A')}")
        print(f"   URL: {response.get('url', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        logger.error("Error en prueba de Webpay", exc_info=True)
        return False

if __name__ == "__main__":
    print("🚀 Iniciando prueba de Webpay con SDK oficial...")
    success = test_webpay_configuration()
    
    if success:
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("📝 Webpay está correctamente configurado para usar el SDK oficial")
    else:
        print("\n💥 Algunas pruebas fallaron")
        print("🔍 Revisa los logs para más detalles")
