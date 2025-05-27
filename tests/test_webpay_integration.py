#!/usr/bin/env python
"""
Script simplificado para probar solo la funcionalidad de Webpay
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plataforma_cursos.settings')

# Eliminar variable de entorno problemática
if 'WEBPAY_API_KEY' in os.environ:
    del os.environ['WEBPAY_API_KEY']

django.setup()

from django.contrib.auth import get_user_model
from carrito.models import Cart, CartItem
from membresias.models import MembershipPlan
from pagos.webpay_rest import crear_transaccion

def test_webpay_integration():
    """Probar integración con Webpay directamente."""
    print("💳 PROBANDO INTEGRACIÓN WEBPAY...")
    # Verificar configuración
    try:
        from decouple import config
        api_key = config("WEBPAY_API_KEY")
        commerce_code = config("WEBPAY_COMMERCE_CODE")
        base_url = config("WEBPAY_BASE_URL")
        
        print("✅ Configuración Webpay cargada correctamente")
        print(f"   - Commerce Code: {commerce_code}")
        print(f"   - API Key: {api_key[:20]}...")
        print(f"   - Base URL: {base_url}")
    except Exception as e:
        print(f"❌ Error cargando configuración Webpay: {e}")
        return False
    
    # Crear transacción de prueba
    try:
        User = get_user_model()
        user = User.objects.filter(email='admin@example.com').first()
        
        if not user:
            print("❌ Usuario no encontrado")
            return False
        
        # Obtener o crear carrito
        cart, created = Cart.objects.get_or_create(user=user, is_active=True)
        
        # Limpiar carrito y agregar una membresía
        cart.items.all().delete()
        membership_plan = MembershipPlan.objects.first()
        
        if not membership_plan:
            print("❌ No hay planes de membresía disponibles")
            return False
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            membership_plan=membership_plan,
            defaults={'quantity': 1}
        )
        print(f"📦 Membresía agregada: {membership_plan.name}")
        
        # Calcular total del carrito
        total = 0
        for item in cart.items.all():
            if item.membership_plan:
                total += item.membership_plan.price * item.quantity
            elif item.course:
                total += item.course.price * item.quantity
        
        print(f"💰 Total carrito: ${total}")
        # Crear transacción de prueba
        buy_order = f"test_{cart.id}_{user.id}"
        session_id = f"session_{user.id}"
        amount = int(total)
        return_url = "http://127.0.0.1:8000/pagos/return/"
        
        print(f"🔍 Datos de transacción:")
        print(f"   - Buy Order: {buy_order}")
        print(f"   - Session ID: {session_id}")
        print(f"   - Amount: {amount}")
        print(f"   - Return URL: {return_url}")
        # Intentar crear transacción
        response = crear_transaccion(
            buy_order=buy_order,
            session_id=session_id,
            amount=amount,
            return_url=return_url
        )
        
        if response:
            print("✅ Transacción creada exitosamente!")
            print(f"🔗 URL Webpay: {response.get('url', 'No URL')}")
            print(f"🎫 Token: {response.get('token', 'No token')[:50]}...")
            return True
        else:
            print("❌ Error creando transacción")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba de integración: {e}")
        return False

def test_dashboard_data():
    """Probar datos del dashboard."""
    print("\n🏠 PROBANDO DATOS DEL DASHBOARD...")
    
    try:
        User = get_user_model()
        user = User.objects.filter(email='admin@example.com').first()
        
        if not user:
            print("❌ Usuario no encontrado")
            return False
        # Verificar membresías activas
        from membresias.models import Membership
        active_memberships = Membership.objects.filter(
            user=user, 
            status='active'
        )
        
        print(f"👤 Usuario: {user.email}")
        print(f"🏷️  Membresías activas: {active_memberships.count()}")
        if active_memberships.exists():
            for membership in active_memberships:
                print(f"   - {membership.plan.name} (hasta {membership.end_date.strftime('%d/%m/%Y')})")
        else:
            print("   - No hay membresías activas")
        # Verificar carrito
        cart = Cart.objects.filter(user=user, is_active=True).first()
        if cart:
            # Calcular total del carrito
            total = 0
            for item in cart.items.all():
                if item.membership_plan:
                    total += item.membership_plan.price * item.quantity
                elif item.course:
                    total += item.course.price * item.quantity
            
            print(f"🛒 Items en carrito: {cart.items.count()}")
            print(f"💰 Total carrito: ${total}")
        else:
            print("🛒 Sin carrito activo")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando dashboard: {e}")
        return False

if __name__ == "__main__":
    webpay_success = test_webpay_integration()
    dashboard_success = test_dashboard_data()
    
    print(f"\n📊 RESULTADOS:")
    print(f"💳 Integración Webpay: {'✅ EXITOSO' if webpay_success else '❌ FALLIDO'}")
    print(f"🏠 Datos dashboard: {'✅ EXITOSO' if dashboard_success else '❌ FALLIDO'}")
    
    if webpay_success and dashboard_success:
        print("\n🎉 ¡INTEGRACIÓN WEBPAY FUNCIONANDO CORRECTAMENTE!")
        print("💡 Puedes probar el flujo completo desde el navegador en:")
        print("   http://127.0.0.1:8000/usuarios/dashboard/")
    else:
        print("\n⚠️  Algunos problemas persisten.")
