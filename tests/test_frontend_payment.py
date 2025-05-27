#!/usr/bin/env python
"""
Script para probar el flujo de pago desde el frontend y diagnosticar problemas.
"""
import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plataforma_cursos.settings')
django.setup()

from carrito.models import Cart, CartItem
from membresias.models import MembershipPlan
from cursos.models import Course

def test_frontend_payment_flow():
    """Probar el flujo de pago desde el frontend."""
    print("🔍 INICIANDO DIAGNÓSTICO DEL FRONTEND...")
    
    # Crear cliente de prueba
    client = Client()
    User = get_user_model()
      # Buscar usuario existente o crear uno
    user = User.objects.filter(email='admin@plataforma-cursos.local').first()
    if not user:
        print("❌ Usuario admin no encontrado. Creando usuario de prueba...")
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!',  # Contraseña que cumple los requisitos
            full_name='Usuario de Prueba'
        )
      # Hacer login
    login_success = client.login(email=user.email, password='admin123')
    if not login_success:
        print("❌ Error en login. Intentando con contraseña alternativa...")
        login_success = client.login(email=user.email, password='TestPass123!')
    
    print(f"✅ Login exitoso: {login_success}")
    
    # Verificar que el carrito esté vacío
    cart, created = Cart.objects.get_or_create(user=user, is_active=True)
    cart.items.all().delete()
    
    # Agregar una membresía al carrito
    membership_plan = MembershipPlan.objects.first()
    if membership_plan:
        print(f"📦 Agregando membresía al carrito: {membership_plan.name}")
        response = client.get(reverse('carrito:add_membership_to_cart', args=[membership_plan.id]))
        print(f"🔍 Status agregar membresía: {response.status_code}")
        
        # Verificar carrito
        response = client.get(reverse('carrito:cart_detail'))
        print(f"🔍 Status ver carrito: {response.status_code}")
        print(f"🔍 Items en carrito: {cart.items.count()}")
        
        # Intentar iniciar pago
        print("💳 Intentando iniciar pago...")
        response = client.get(reverse('pagos:initiate_cart_payment'))
        print(f"🔍 Status iniciar pago: {response.status_code}")
        
        if response.status_code == 302:
            print(f"🔀 Redirección a: {response.url}")
        elif response.status_code == 500:
            print("❌ Error 500 en el servidor")
            # Intentar obtener más detalles del error
            try:
                response = client.get(reverse('pagos:initiate_cart_payment'), follow=True)
                print(f"🔍 Status después de follow: {response.status_code}")
            except Exception as e:
                print(f"❌ Error específico: {e}")
        else:
            print(f"⚠️  Status inesperado: {response.status_code}")
            
        return response.status_code
    else:
        print("❌ No hay planes de membresía disponibles")
        return 404

def test_webpay_config():
    """Probar la configuración de Webpay."""
    print("\n🔧 VERIFICANDO CONFIGURACIÓN DE WEBPAY...")
    
    from pagos.webpay_rest import WEBPAY_BASE_URL, COMMERCE_CODE, API_KEY
    
    print(f"📍 Base URL: {WEBPAY_BASE_URL}")
    print(f"🏪 Commerce Code: {COMMERCE_CODE}")
    print(f"🔑 API Key: {API_KEY[:10]}...{API_KEY[-10:] if len(API_KEY) > 20 else API_KEY}")
    
    # Probar conexión básica
    try:
        import requests
        from pagos.webpay_rest import HEADERS
        
        test_url = f"{WEBPAY_BASE_URL}/transactions"
        print(f"🔍 Probando conexión a: {test_url}")
        print(f"🔍 Headers: {HEADERS}")
        
        # Hacer una prueba básica (que debería fallar pero nos dará info)
        response = requests.post(test_url, json={}, headers=HEADERS, timeout=10)
        print(f"🔍 Status de prueba: {response.status_code}")
        print(f"🔍 Respuesta: {response.text[:200]}...")
        
    except Exception as e:
        print(f"❌ Error en conexión Webpay: {e}")

if __name__ == "__main__":
    test_webpay_config()
    test_frontend_payment_flow()
    print("\n✅ DIAGNÓSTICO COMPLETADO")
