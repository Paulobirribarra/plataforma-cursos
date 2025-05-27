#!/usr/bin/env python
"""
Script simple para verificar las credenciales de Webpay.
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plataforma_cursos.settings')
django.setup()

import requests
from pagos.webpay_rest import crear_transaccion, WEBPAY_BASE_URL, COMMERCE_CODE, API_KEY, HEADERS

def test_webpay_connection():
    """Probar conexión con Webpay."""
    print("🔧 VERIFICANDO CREDENCIALES DE WEBPAY...")
    print(f"📍 Base URL: {WEBPAY_BASE_URL}")
    print(f"🏪 Commerce Code: {COMMERCE_CODE}")
    print(f"🔑 API Key: {API_KEY}")
    print(f"🔍 Headers: {HEADERS}")
    
    # Probar crear una transacción de prueba
    try:
        print("\n💳 Probando crear transacción...")
        result = crear_transaccion(
            buy_order="test123456789",
            session_id="test_session",
            amount=1000,
            return_url="http://localhost:8000/pagos/webpay/return/"
        )
        
        print(f"✅ Transacción creada exitosamente!")
        print(f"🔗 Token: {result.get('token', 'N/A')}")
        print(f"🌐 URL: {result.get('url', 'N/A')}")
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error HTTP: {e}")
        print(f"🔍 Status Code: {e.response.status_code}")
        print(f"🔍 Response: {e.response.text}")
        
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    test_webpay_connection()
