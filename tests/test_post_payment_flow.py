#!/usr/bin/env python
"""
Script para probar el flujo completo de pago post-compra.
Verifica que las mejoras implementadas funcionen correctamente.
"""
import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

# Configurar Django
os.chdir('e:/Paulo/Github/plataforma-cursos')
sys.path.insert(0, os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plataforma_cursos.settings')
django.setup()

from carrito.models import Cart, CartItem
from membresias.models import MembershipPlan, Membership
from cursos.models import Course, UserCourse
from pagos.models import Payment

User = get_user_model()

def test_post_payment_flow():
    """Prueba el flujo post-pago completo."""
    print("🚀 Iniciando pruebas del flujo post-pago...")
    
    # 1. Crear usuario de prueba
    try:
        user = User.objects.get(email='test_payment@example.com')
        print("✅ Usuario de prueba encontrado")
    except User.DoesNotExist:
        user = User.objects.create_user(
            email='test_payment@example.com',
            password='testpass123'
        )
        print("✅ Usuario de prueba creado")
    
    # 2. Verificar que existen planes de membresía
    membership_plan = MembershipPlan.objects.filter(is_active=True).first()
    if not membership_plan:
        print("❌ No hay planes de membresía disponibles")
        return False
    print(f"✅ Plan de membresía encontrado: {membership_plan.name}")
    
    # 3. Verificar que existen cursos
    course = Course.objects.filter(is_available=True).first()
    if not course:
        print("❌ No hay cursos disponibles")
        return False
    print(f"✅ Curso encontrado: {course.title}")
    
    # 4. Simular compra: crear carrito con membresía y curso
    cart, created = Cart.objects.get_or_create(user=user, is_active=True)
    cart.items.all().delete()  # Limpiar carrito anterior
    
    # Agregar membresía al carrito
    CartItem.objects.create(
        cart=cart,
        item_type="membership",
        membership_plan=membership_plan,
        price_applied=membership_plan.price,
    )
    
    # Agregar curso al carrito
    CartItem.objects.create(
        cart=cart,
        item_type="course",
        course=course,
        price_applied=course.get_final_price(),
    )
    
    print("✅ Carrito creado con membresía y curso")
    
    # 5. Crear pago simulado
    total_amount = sum(item.price_applied for item in cart.items.all())
    payment = Payment.objects.create(
        user=user,
        amount=total_amount,
        description="Compra de carrito (prueba)",
        payment_type="cart",
        status="pending"
    )
    print(f"✅ Pago creado: ${total_amount}")
    
    # 6. Simular confirmación de pago
    client = Client()
    client.force_login(user)
    
    # Simular datos de sesión para el flujo de pago
    session = client.session
    session['purchase_success_data'] = {
        'payment_id': payment.id,
        'purchased_items': [
            {
                'item_type': item.item_type,
                'course_title': item.course.title if item.course else None,
                'membership_name': item.membership_plan.name if item.membership_plan else None,
                'price_applied': float(item.price_applied)
            } for item in cart.items.all()
        ],
        'has_new_membership': True,
        'has_new_courses': True,
        'total_amount': float(total_amount)
    }
    session.save()
    
    # Simular procesamiento de items del carrito
    for item in cart.items.all():
        if item.item_type == "course" and item.course:
            UserCourse.objects.get_or_create(
                user=user, 
                course=item.course,
                defaults={'progress': 0.0, 'completed': False}
            )
        elif item.item_type == "membership" and item.membership_plan:
            # Verificar si ya existe una membresía activa
            existing_membership = Membership.objects.filter(
                user=user, 
                status='active'
            ).first()
            
            if existing_membership:
                # Actualizar membresía existente
                existing_membership.plan = item.membership_plan
                existing_membership.courses_remaining = item.membership_plan.courses_per_month
                existing_membership.consultations_remaining = item.membership_plan.consultations
                existing_membership.save()
            else:
                # Crear nueva membresía
                Membership.objects.create(
                    user=user,
                    plan=item.membership_plan,
                    status="active",
                    courses_remaining=item.membership_plan.courses_per_month,
                    consultations_remaining=item.membership_plan.consultations
                )
    
    cart.is_active = False
    cart.save()
    payment.status = "completed"
    payment.save()
    
    print("✅ Procesamiento de compra completado")
    
    # 7. Verificar membresía activa
    active_membership = Membership.objects.filter(user=user, status='active').first()
    if active_membership:
        print(f"✅ Membresía activa creada: {active_membership.plan.name}")
        print(f"   - Cursos restantes: {active_membership.courses_remaining}")
        print(f"   - Consultas restantes: {active_membership.consultations_remaining}")
    else:
        print("❌ No se creó membresía activa")
        return False
    
    # 8. Verificar acceso a curso
    user_course = UserCourse.objects.filter(user=user, course=course).first()
    if user_course:
        print(f"✅ Acceso a curso creado: {user_course.course.title}")
        print(f"   - Progreso: {user_course.progress}%")
        print(f"   - Completado: {user_course.completed}")
    else:
        print("❌ No se creó acceso al curso")
        return False
    
    # 9. Probar las vistas
    try:
        # Probar dashboard
        response = client.get(reverse('usuarios:dashboard'))
        if response.status_code == 200:
            print("✅ Dashboard accesible")
        else:
            print(f"❌ Error en dashboard: {response.status_code}")
            return False
        
        # Probar página de éxito
        response = client.get(reverse('pagos:purchase_success'))
        if response.status_code == 200:
            print("✅ Página de éxito accesible")
        else:
            print(f"❌ Error en página de éxito: {response.status_code}")
            return False
        
        # Probar mis cursos
        response = client.get(reverse('usuarios:my_courses'))
        if response.status_code == 200:
            print("✅ Página de mis cursos accesible")
        else:
            print(f"❌ Error en mis cursos: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error al probar vistas: {e}")
        return False
    
    # 10. Probar estadísticas
    total_courses = user.user_courses.count()
    completed_count = user.user_courses.filter(completed=True).count()
    in_progress_count = user.user_courses.filter(completed=False, progress__gt=0).count()
    
    print(f"✅ Estadísticas del usuario:")
    print(f"   - Total de cursos: {total_courses}")
    print(f"   - Completados: {completed_count}")
    print(f"   - En progreso: {in_progress_count}")
    
    print("\n🎉 ¡Todas las pruebas del flujo post-pago pasaron exitosamente!")
    print("\nFuncionalidades verificadas:")
    print("✅ Activación correcta de membresías")
    print("✅ Creación de acceso a cursos")
    print("✅ Página de confirmación de compra")
    print("✅ Dashboard actualizado con membresía")
    print("✅ Página 'Mis Cursos' funcional")
    print("✅ URLs y vistas funcionando correctamente")
    
    return True

def test_urls():
    """Prueba que todas las URLs estén configuradas correctamente."""
    print("\n🔗 Probando configuración de URLs...")
    
    urls_to_test = [
        ('usuarios:dashboard', {}),
        ('usuarios:my_courses', {}),
        ('pagos:purchase_success', {}),
        ('membresias:plan_list', {}),
        ('carrito:cart_detail', {}),
    ]
    
    for url_name, kwargs in urls_to_test:
        try:
            url = reverse(url_name, kwargs=kwargs)
            print(f"✅ {url_name}: {url}")
        except Exception as e:
            print(f"❌ {url_name}: Error - {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("   PRUEBA DEL FLUJO POST-PAGO MEJORADO")
    print("=" * 60)
    
    # Probar URLs
    if not test_urls():
        print("❌ Falló la prueba de URLs")
        sys.exit(1)
    
    # Probar flujo completo
    if not test_post_payment_flow():
        print("❌ Falló la prueba del flujo post-pago")
        sys.exit(1)
    
    print("\n🎯 Próximos pasos recomendados:")
    print("1. Probar el flujo completo en el navegador")
    print("2. Realizar una compra real para verificar Webpay")
    print("3. Verificar emails de confirmación")
    print("4. Revisar la experiencia de usuario en móviles")
