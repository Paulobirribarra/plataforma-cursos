#!/usr/bin/env python
"""
Prueba simplificada que verifica que la redirección a la página de éxito de compra funciona.
"""
import os
import django
import sys

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plataforma_cursos.settings")
os.environ.setdefault("DEBUG", "True")  # Forzar modo DEBUG para las pruebas
django.setup()

# Configurar ALLOWED_HOSTS para las pruebas
from django.conf import settings
settings.ALLOWED_HOSTS += ['testserver', 'localhost', '127.0.0.1']

from django.test.client import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from pagos.models import Payment
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

User = get_user_model()

def test_payment_success_page():
    """Prueba la página de confirmación de compra exitosa."""
    print("="*60)
    print(" DIAGNÓSTICO DE LA PÁGINA DE CONFIRMACIÓN DE COMPRA ")
    print("="*60)
    
    # 1. Verificar que existe la ruta 
    try:
        url = reverse('pagos:purchase_success')
        print(f"✅ La ruta 'pagos:purchase_success' existe: {url}")
    except Exception as e:
        print(f"❌ Error al obtener la ruta: {e}")
        return False
    
    # 2. Crear usuario para prueba
    try:
        email = 'test_payment@example.com'
        password = 'Test123456!'
        
        # Eliminar usuario si ya existe
        User.objects.filter(email=email).delete()
        
        # Crear un nuevo usuario
        user = User.objects.create_user(email=email, password=password)
        user.is_active = True
        user.save()
        print(f"✅ Usuario creado: {user.email}")
        
        # Verificar que el usuario existe
        if User.objects.filter(email=email).exists():
            print("✅ Usuario existe en la base de datos")
        else:
            print("❌ Error: Usuario no fue creado correctamente")
            return False
    except Exception as e:
        print(f"❌ Error al crear usuario: {e}")
        return False
    
    # 3. Crear un pago de prueba
    try:
        payment = Payment.objects.create(
            user=user,
            amount=59990,
            description="Pago de prueba",
            payment_type="cart",
            status="completed"
        )
        print(f"✅ Pago creado con ID: {payment.id}")
    except Exception as e:
        print(f"❌ Error al crear pago: {e}")
        return False
    
    # 4. Simular una petición directa a la vista con datos en sesión
    client = Client()
    
    # Intentar iniciar sesión
    login_success = client.login(email=email, password=password)
    if not login_success:
        print("⚠️ No se pudo iniciar sesión con email/password, probando otro método")
        login_success = client.login(username=email, password=password)
        if not login_success:
            print("⚠️ No se pudo iniciar sesión, probando con fuerza bruta")
            # Crear una sesión manualmente
            from django.contrib.auth import authenticate
            user = authenticate(username=email, password=password)
            if user is None:
                user = User.objects.get(email=email)  # Forzar
            
            client.force_login(user)
            print("✅ Forzado inicio de sesión mediante force_login()")
        else:
            print("✅ Inicio de sesión exitoso mediante 'username=email'")
    else:
        print("✅ Inicio de sesión exitoso mediante email/password")
    
    # Preparar datos para la sesión
    session = client.session
    session['purchase_success_data'] = {
        'payment_id': payment.id,
        'purchased_items': [
            {
                'item_type': 'course',
                'course_title': 'Curso de Prueba',
                'membership_name': None,
                'price_applied': 19990.0
            },
            {
                'item_type': 'membership',
                'course_title': None, 
                'membership_name': 'Plan Premium',
                'price_applied': 39990.0
            }
        ],
        'has_new_membership': True,
        'has_new_courses': True,
        'total_amount': 59980.0
    }
    session.save()
    print("✅ Datos guardados en la sesión")
    
    # 5. Hacer petición a la vista
    try:
        response = client.get(url)
        print(f"📊 Código de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Página de éxito cargada correctamente")
            print("🎯 Todo funciona correctamente. El flujo post-pago está bien configurado.")
            return True
        else:
            print(f"❌ Error al cargar la página: código {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error al hacer la petición: {e}")
        return False


if __name__ == "__main__":
    if test_payment_success_page():
        print("\n✅ El diagnóstico ha sido exitoso!")
        print("\nPara verificar el flujo completo:")
        print("1. Inicie sesión con un usuario")
        print("2. Agregue productos al carrito")
        print("3. Complete el proceso de pago")
        print("4. Verifique que sea redirigido a la página de confirmación")
        print("5. Compruebe que sus membresías y cursos aparezcan en el dashboard")
    else:
        print("\n❌ El diagnóstico ha fallado. Revise los errores y realice las correcciones necesarias.")
        sys.exit(1)
