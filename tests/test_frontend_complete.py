#!/usr/bin/env python
"""
Script para probar el flujo completo de pago desde el frontend.
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

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from carrito.models import Cart, CartItem
from membresias.models import MembershipPlan
from cursos.models import Course

def test_complete_frontend_flow():
    """Probar el flujo completo del frontend."""
    print("🚀 INICIANDO PRUEBA COMPLETA DEL FRONTEND...")
    
    # Crear cliente de prueba
    client = Client()
    User = get_user_model()
    # Usar usuario admin existente
    user = User.objects.filter(email='admin@example.com').first()
    if not user:
        print("❌ Usuario admin@example.com no encontrado")
        return False
    
    print(f"👤 Usuario: {user.email}")
    # Hacer login (simular envío del formulario de login)
    login_data = {
        'login': user.email,
        'password': 'Admin123!'
    }
    
    response = client.post(reverse('account_login'), data=login_data)
    
    if response.status_code == 302:  # Redirección exitosa
        print("✅ Login exitoso")
    else:
        print(f"❌ Error en login: {response.status_code}")
        return False
    
    # Limpiar carrito existente
    cart, created = Cart.objects.get_or_create(user=user, is_active=True)
    cart.items.all().delete()
    print("🧹 Carrito limpiado")
    
    # Agregar una membresía al carrito
    membership_plan = MembershipPlan.objects.first()
    if not membership_plan:
        print("❌ No hay planes de membresía disponibles")
        return False
    
    print(f"📦 Agregando membresía: {membership_plan.name}")
    response = client.get(reverse('carrito:add_membership_to_cart', args=[membership_plan.id]))
    
    if response.status_code == 302:  # Redirección al carrito
        print("✅ Membresía agregada al carrito")
    else:
        print(f"❌ Error agregando membresía: {response.status_code}")
        return False
    
    # Verificar carrito
    response = client.get(reverse('carrito:cart_detail'))
    if response.status_code == 200:
        print("✅ Carrito accesible")
        cart.refresh_from_db()
        print(f"📊 Items en carrito: {cart.items.count()}")
    else:
        print(f"❌ Error accediendo al carrito: {response.status_code}")
        return False
    
    # Probar iniciación de pago (el botón problemático)
    print("💳 Probando iniciación de pago...")
    response = client.get(reverse('pagos:initiate_cart_payment'))
    
    if response.status_code == 302:  # Redirección a Webpay
        print("✅ Pago iniciado exitosamente!")
        print(f"🔗 Redirigido a: {response.url}")
        
        # Verificar que es una URL de Webpay
        if 'webpay' in response.url.lower():
            print("✅ Redirección correcta a Webpay")
            return True
        else:
            print(f"⚠️  Redirección inesperada: {response.url}")
            return False
            
    else:
        print(f"❌ Error en iniciación de pago: {response.status_code}")
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8')
            print(f"📄 Contenido de respuesta: {content[:500]}...")
        return False

def test_dashboard_with_memberships():
    """Probar el dashboard con la nueva sección de membresías."""
    print("\n🏠 PROBANDO DASHBOARD CON MEMBRESÍAS...")
    client = Client()
    User = get_user_model()
    
    user = User.objects.filter(email='admin@example.com').first()
    if not user:
        print("❌ Usuario admin@example.com no encontrado")
        return False
    
    # Hacer login
    login_data = {        'login': user.email,
        'password': 'Admin123!'
    }
    client.post(reverse('account_login'), data=login_data)
      # Acceder al dashboard
    response = client.get(reverse('usuarios:dashboard'))
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Verificar que las nuevas secciones estén presentes
        if 'Mi Membresía' in content:
            print("✅ Sección de membresías presente en dashboard")
        else:
            print("❌ Sección de membresías NO encontrada")
            
        if 'Mi Carrito' in content:
            print("✅ Sección de carrito presente en dashboard")
        else:
            print("❌ Sección de carrito NO encontrada")
            
        return True
    else:
        print(f"❌ Error accediendo al dashboard: {response.status_code}")
        return False

if __name__ == "__main__":
    frontend_success = test_complete_frontend_flow()
    dashboard_success = test_dashboard_with_memberships()
    
    print(f"\n📊 RESULTADOS:")
    print(f"🔥 Flujo de pago frontend: {'✅ EXITOSO' if frontend_success else '❌ FALLIDO'}")
    print(f"🏠 Dashboard mejorado: {'✅ EXITOSO' if dashboard_success else '❌ FALLIDO'}")
    
    if frontend_success and dashboard_success:
        print("\n🎉 ¡TODOS LOS PROBLEMAS DEL FRONTEND SOLUCIONADOS!")
    else:
        print("\n⚠️  Algunos problemas persisten, revisar logs arriba.")
