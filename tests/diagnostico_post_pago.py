#!/usr/bin/env python
"""
Script de diagnóstico para el flujo post-pago.
Este script simula el proceso de compra y redireccionamiento a la página de éxito.
"""

import os
import django

# Configuración inicial de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plataforma_cursos.settings")
django.setup()

from django.test.client import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from carrito.models import Cart, CartItem
from pagos.models import Payment
from membresias.models import Membership, MembershipPlan
from cursos.models import Course, UserCourse
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

User = get_user_model()

def simular_compra_y_redireccion():
    """Simula el proceso de compra y redirección a la página de éxito."""
    
    # Crear usuario de prueba si no existe
    USERNAME = "test@example.com"
    PASSWORD = "testpassword123"
    
    try:
        usuario = User.objects.get(email=USERNAME)
        logging.info(f"Usuario encontrado: {usuario}")
    except User.DoesNotExist:
        usuario = User.objects.create_user(
            email=USERNAME,
            password=PASSWORD,
        )
        usuario.is_active = True
        usuario.save()
        logging.info(f"Usuario creado: {usuario}")

    # Asegurarse de que hay al menos un plan y un curso
    if not MembershipPlan.objects.exists():
        logging.error("No hay planes de membresía disponibles para la prueba")
        return False
    
    if not Course.objects.exists():
        logging.error("No hay cursos disponibles para la prueba")
        return False
    
    plan = MembershipPlan.objects.first()
    curso = Course.objects.first()
    
    # Limpiar datos de prueba anteriores
    Payment.objects.filter(user=usuario).delete()
    Cart.objects.filter(user=usuario).delete()
    Membership.objects.filter(user=usuario).delete()
    UserCourse.objects.filter(user=usuario, course=curso).delete()
    
    # Crear carrito con membresía y curso
    cart = Cart.objects.create(user=usuario, is_active=True)
    CartItem.objects.create(
        cart=cart,
        item_type="membership",
        membership_plan=plan,
        price_applied=plan.price
    )
    CartItem.objects.create(
        cart=cart,
        item_type="course",
        course=curso,
        price_applied=curso.get_final_price()
    )
    
    # Crear pago
    total = sum(item.price_applied for item in cart.items.all())
    payment = Payment.objects.create(
        user=usuario,
        amount=total,
        description=f"Prueba: Membresía {plan.name} y Curso {curso.title}",
        payment_type="cart",
        status="pending"
    )
    payment.status = "completed"
    payment.save()
    
    # Procesar ítems del carrito (lógica de webpay_return)
    purchased_items = list(cart.items.all())
    has_new_membership = False
    has_new_courses = False
    
    # Crear acceso a curso
    UserCourse.objects.create(
        user=usuario,
        course=curso,
        progress=0.0,
        completed=False
    )
    has_new_courses = True
    
    # Crear membresía
    Membership.objects.create(
        user=usuario,
        plan=plan,
        status="active",
        courses_remaining=plan.courses_per_month,
        consultations_remaining=plan.consultations
    )
    has_new_membership = True
    
    # Marcar carrito como inactivo
    cart.is_active = False
    cart.save()
      # Iniciar sesión con el cliente de prueba
    client = Client()
    logged_in = client.login(email=USERNAME, password=PASSWORD)
    if not logged_in:
        logging.error("No se pudo iniciar sesión")
        return False
    
    # Preparar datos para la sesión
    session = client.session
    session['purchase_success_data'] = {
        'payment_id': payment.id,
        'purchased_items': [
            {
                'item_type': item.item_type,
                'course_title': item.course.title if item.course else None,
                'membership_name': item.membership_plan.name if item.membership_plan else None,
                'price_applied': float(item.price_applied)
            } for item in purchased_items
        ],
        'has_new_membership': has_new_membership,
        'has_new_courses': has_new_courses,
        'total_amount': float(payment.amount)
    }
    session.save()
    
    # Obtener URL de la página de éxito
    success_url = reverse('pagos:purchase_success')
    
    # Hacer la petición para verificar que la página funciona
    response = client.get(success_url)
    
    if response.status_code == 200:
        logging.info("✅ Página de éxito cargada correctamente")
        
        # Verificar también el perfil y dashboard
        dashboard_url = reverse('usuarios:dashboard')
        dashboard_response = client.get(dashboard_url)
        
        if dashboard_response.status_code == 200:
            logging.info("✅ Dashboard cargado correctamente")
        else:
            logging.error(f"❌ Error al cargar dashboard: {dashboard_response.status_code}")
        
        my_courses_url = reverse('usuarios:my_courses')
        courses_response = client.get(my_courses_url)
        
        if courses_response.status_code == 200:
            logging.info("✅ Página de mis cursos cargada correctamente")
        else:
            logging.error(f"❌ Error al cargar mis cursos: {courses_response.status_code}")
            
        logging.info(f"\nInstrucciones para verificar manualmente:\n" + 
              f"1. Inicia sesión con {USERNAME} / {PASSWORD}\n" +
              f"2. Accede a /pagos/exito/\n" +
              f"3. Verifica que el dashboard muestre tu membresía activa\n" +
              f"4. Verifica que 'Mis cursos' muestre el curso comprado")
        
        return True
    else:
        logging.error(f"❌ Error al cargar la página de éxito: {response.status_code}")
        return False

if __name__ == '__main__':
    print("="*60)
    print(" DIAGNÓSTICO DEL FLUJO POST-PAGO ")
    print("="*60)
    
    if simular_compra_y_redireccion():
        print("\n✅ El diagnóstico del flujo post-pago ha sido exitoso!")
    else:
        print("\n❌ El diagnóstico del flujo post-pago ha fallado. Revisa los logs para más detalles.")
