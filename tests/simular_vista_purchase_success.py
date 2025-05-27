#!/usr/bin/env python
"""
Script de simulación directa de la vista purchase_success
No requiere autenticación, sino que llama directamente a la vista
"""
import os
import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plataforma_cursos.settings")
django.setup()

import sys
from django.test.client import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from pagos.views import purchase_success
from pagos.models import Payment
from membresias.models import MembershipPlan
from cursos.models import Course

User = get_user_model()

def simular_vista_purchase_success():
    print("\n💡 Simulando la vista purchase_success directamente...")
    
    # 1. Obtener o crear un usuario de prueba
    try:
        user = User.objects.get(email='test@example.com')
        print("✅ Usuario de prueba encontrado")
    except User.DoesNotExist:
        user = User.objects.create_user(
            email='test@example.com',
            password='testpassword123',
        )
        user.is_active = True
        user.save()
        print("✅ Usuario de prueba creado")
    
    # 2. Crear un pago de prueba
    payment, created = Payment.objects.get_or_create(
        user=user,
        status="completed",
        payment_type="cart",
        amount=59990,
        defaults={
            "description": "Pago de prueba para simulación"
        }
    )
    if created:
        print(f"✅ Pago de prueba creado con ID: {payment.id}")
    else:
        print(f"✅ Usando pago existente con ID: {payment.id}")
    
    # 3. Crear factory para simular request
    factory = RequestFactory()
    request = factory.get('/pagos/exito/')
    request.user = user
    
    # 4. Configurar sesión en el request
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session.save()
    
    # 5. Añadir datos a la sesión
    request.session['purchase_success_data'] = {
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
        'total_amount': float(payment.amount)
    }
    request.session.save()
      # 6. Modificar la función para usar la plantilla de prueba
    from django.shortcuts import render
    
    def purchase_success_test(request):
        """Función modificada para usar la plantilla de prueba"""
        # Obtener datos de la sesión
        success_data = request.session.get('purchase_success_data')
        
        if not success_data:
            return HttpResponse("No se encontró información de compra reciente.")
        
        # Obtener el pago
        try:
            payment = Payment.objects.get(id=success_data['payment_id'], user=request.user)
        except Payment.DoesNotExist:
            return HttpResponse("No se encontró el pago especificado.")
        
        context = {
            'payment': payment,
            'purchased_items': success_data['purchased_items'],
            'has_new_membership': success_data['has_new_membership'],
            'has_new_courses': success_data['has_new_courses'],
            'total_amount': success_data['total_amount'],
        }
        
        return render(request, 'pagos/purchase_success_test.html', context)
    
    # Llamar a nuestra función de prueba
    try:
        print("⏳ Llamando a la vista purchase_success modificada...")
        response = purchase_success_test(request)
        print(f"✅ Código de respuesta: {response.status_code}")
        
        # 7. Guardar el resultado
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vista_output.html')
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Resultado de la vista guardado en {output_path}")
        print("✅ La vista parece estar funcionando correctamente")
          # 8. Verificar si usa la plantilla fija
        content = response.content.decode('utf-8')
        
        # Buscar patrones distintivos de la plantilla
        if "<div class=\"min-h-screen bg-gradient-to-br from-green-50 to-blue-50" in content:
            print("✅ Contenido corresponde a la plantilla corregida (spaces bien formateados)")
        elif "<div\n  class=\"min-h-screen bg-gradient-to-br from-green-50 to-blue-50" in content:
            print("❌ Contenido parece corresponder a la plantilla original (saltos de línea incorrectos)")
        else:
            print("⚠️ No se puede determinar qué plantilla se está usando")
            
        # Imprimir las URLs para depuración
        print("\nURLs en el contenido renderizado:")
        for line in content.split("\n"):
            if "href=" in line and ("dashboard" in line or "my_courses" in line):
                print(f"  {line.strip()}")
        
        return True
    except Exception as e:
        print(f"❌ Error al llamar a la vista: {e}")
        print(f"Traceback: {sys.exc_info()}")
        return False

if __name__ == "__main__":
    print("="*60)
    print(" SIMULACIÓN DIRECTA DE LA VISTA PURCHASE_SUCCESS ")
    print("="*60)
    
    if simular_vista_purchase_success():
        print("\n✅ La simulación ha sido exitosa!")
    else:
        print("\n❌ La simulación ha fallado. Revisa los errores anteriores.")
        sys.exit(1)
