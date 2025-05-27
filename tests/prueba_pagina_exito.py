#!/usr/bin/env python
"""
Script de diagnóstico simplificado para probar la redirección a la página de éxito.
"""
import os
import django
import sys

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plataforma_cursos.settings")
django.setup()

# Importar modelos y vistas
from django.test.client import Client
from django.urls import reverse
from django.contrib.auth import get_user_model

# Obtener el modelo de usuario
User = get_user_model()

def test_success_page():
    """Prueba la página de éxito de compra."""
    print("\n💡 Probando página de éxito...")

    # 1. Crear/obtener un usuario de prueba
    try:
        user = User.objects.get(email='test@example.com')
        print("✅ Usuario de prueba encontrado")
    except User.DoesNotExist:
        try:
            # Crear el usuario
            user = User.objects.create_user(
                email='test@example.com',
                password='testpassword123',
            )
            user.is_active = True
            user.save()
            print("✅ Usuario de prueba creado")
        except Exception as e:
            print(f"❌ Error al crear usuario: {e}")
            return False    # 2. Iniciar sesión con el cliente de prueba
    client = Client()
    try:
        # Django-allauth utiliza email en lugar de username
        login_successful = client.login(email='test@example.com', password='testpassword123')
        if login_successful:
            print("✅ Inicio de sesión exitoso")
        else:
            print("❌ Error de inicio de sesión, intentando forzar inicio de sesión")
            # Intentar forzar el inicio de sesión directamente
            from django.contrib.auth import authenticate, login
            from django.test.client import RequestFactory
            factory = RequestFactory()
            request = factory.get('/')
            request.session = client.session
            user = authenticate(request, email='test@example.com', password='testpassword123')
            if user is not None:
                login(request, user)
                client.cookies = request.cookies
                client.session = request.session
                print("✅ Inicio de sesión forzado exitoso")
            else:
                print("❌ Error de autenticación")
                return False
    except Exception as e:
        print(f"❌ Error durante el inicio de sesión: {e}")
        return False

    # 3. Configurar datos de prueba en la sesión
    try:
        session = client.session
        session['purchase_success_data'] = {
            'payment_id': 1,  # ID ficticio
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
                    'membership_name': 'Plan Básico',
                    'price_applied': 39990.0
                }
            ],
            'has_new_membership': True,
            'has_new_courses': True,
            'total_amount': 59980.0
        }
        session.save()
        print("✅ Datos de prueba guardados en la sesión")
    except Exception as e:
        print(f"❌ Error al configurar la sesión: {e}")
        return False

    # 4. Intentar acceder a la página de éxito
    try:
        url = reverse('pagos:purchase_success')
        print(f"🔍 Accediendo a URL: {url}")
        
        response = client.get(url)
        print(f"📊 Código de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Página de éxito cargada correctamente")
            print("✅ El flujo post-pago está configurado correctamente")
            print("\n🎯 Próximos pasos:")
            print("1. Verificar que la página muestre correctamente los datos")
            print("2. Comprobar el funcionamiento completo haciendo una compra real")
            return True
        else:
            print("❌ Error al cargar la página de éxito")
            return False
    except Exception as e:
        print(f"❌ Error al acceder a la página de éxito: {e}")
        print(f"Traceback: {sys.exc_info()}")
        return False

if __name__ == "__main__":
    print("="*60)
    print(" DIAGNÓSTICO SIMPLIFICADO DEL FLUJO POST-PAGO ")
    print("="*60)
    
    if test_success_page():
        print("\n✅ Las pruebas han sido exitosas!")
    else:
        print("\n❌ Las pruebas han fallado. Revisa los errores anteriores.")
        sys.exit(1)
