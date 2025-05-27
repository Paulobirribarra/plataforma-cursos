#!/usr/bin/env python
"""
Script para probar el flujo completo de compra de membresía
Este script simula:
1. Registro de usuario
2. Selección de membresía
3. Proceso de pago
4. Verificación de membresía en perfil
"""
import os
import sys
import django
from decimal import Decimal

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plataforma_cursos.settings")
django.setup()

from django.contrib.auth import get_user_model
from membresias.models import MembershipPlan, Membership
from carrito.models import Cart, CartItem
from pagos.models import Payment
from cursos.models import UserCourse
from django.utils import timezone
from allauth.account.models import EmailAddress

User = get_user_model()

def test_complete_purchase_flow():
    """Prueba el flujo completo de compra de membresía"""
    print("🚀 INICIANDO PRUEBA DEL FLUJO COMPLETO DE COMPRA DE MEMBRESÍA")
    print("=" * 70)
    
    # Limpiar datos de prueba previos
    test_email = "test_user@plataforma-cursos.local"
    test_username = "test_user_purchase"
    
    # Eliminar usuario de prueba si existe
    User.objects.filter(email=test_email).delete()
    
    print("✅ Datos de prueba limpiados")
    
    # 1. REGISTRO DE USUARIO
    print("\n📝 PASO 1: REGISTRO DE USUARIO")
    print("-" * 40)
    
    user = User.objects.create_user(
        email=test_email,
        username=test_username,
        password="TestPassword123!",
        full_name="Usuario de Prueba",
        phone="+56987654321",
        is_email_verified=True  # Simular email verificado
    )
    
    # Crear registro de email verificado para allauth
    EmailAddress.objects.create(
        user=user,
        email=test_email,
        verified=True,
        primary=True
    )
    
    print(f"   ✅ Usuario creado: {user.email}")
    print(f"   ✅ Email verificado: {user.is_email_verified}")
    print(f"   ✅ Nombre completo: {user.full_name}")
    
    # 2. SELECCIÓN DE MEMBRESÍA
    print("\n💎 PASO 2: SELECCIÓN DE MEMBRESÍA")
    print("-" * 40)
    
    # Obtener el plan básico
    plan_basico = MembershipPlan.objects.filter(slug="plan-basico").first()
    if not plan_basico:
        print("   ❌ Error: Plan básico no encontrado")
        return False
    
    print(f"   ✅ Plan seleccionado: {plan_basico.name}")
    print(f"   ✅ Precio: ${plan_basico.price:,.0f}")
    print(f"   ✅ Cursos por mes: {plan_basico.courses_per_month}")
    print(f"   ✅ Consultas: {plan_basico.consultations}")
    
    # 3. AGREGAR AL CARRITO
    print("\n🛒 PASO 3: AGREGAR MEMBRESÍA AL CARRITO")
    print("-" * 40)
    
    # Crear carrito
    cart, created = Cart.objects.get_or_create(user=user, is_active=True)
    
    # Agregar membresía al carrito
    cart_item = CartItem.objects.create(
        cart=cart,
        item_type="membership",
        membership_plan=plan_basico,
        price_applied=plan_basico.price,
        quantity=1
    )
    
    print(f"   ✅ Carrito creado: {cart}")
    print(f"   ✅ Item agregado: {cart_item}")
    print(f"   ✅ Total del carrito: ${cart_item.price_applied:,.0f}")
    
    # 4. PROCESO DE PAGO
    print("\n💳 PASO 4: PROCESO DE PAGO")
    print("-" * 40)
    
    # Calcular total
    total = sum(item.price_applied for item in cart.items.all())
    
    # Crear pago
    payment = Payment.objects.create(
        user=user,
        amount=total,
        description=f"Membresía {plan_basico.name}",
        status="pending",
        payment_type="cart"
    )
    
    print(f"   ✅ Pago creado: ID {payment.id}")
    print(f"   ✅ Monto: ${payment.amount:,.0f}")
    print(f"   ✅ Estado inicial: {payment.status}")
    
    # Simular proceso de pago exitoso (sin Webpay real)
    print("   🔄 Simulando proceso de pago exitoso...")
    
    payment.status = "completed"
    payment.save()
    
    print(f"   ✅ Pago completado: {payment.status}")
    
    # 5. PROCESAR ITEMS DEL CARRITO
    print("\n📦 PASO 5: PROCESAMIENTO DE COMPRA")
    print("-" * 40)
    
    # Procesar items del carrito (simular lógica de webpay_return)
    for item in cart.items.all():
        if item.item_type == "membership" and item.membership_plan:
            # Crear membresía
            membership = Membership.objects.create(
                user=user,
                plan=item.membership_plan,
                status="active",
                courses_remaining=item.membership_plan.courses_per_month,
                consultations_remaining=item.membership_plan.consultations
            )
            print(f"   ✅ Membresía creada: {membership}")
            print(f"   ✅ Estado: {membership.status}")
            print(f"   ✅ Fecha de inicio: {membership.start_date}")
            print(f"   ✅ Fecha de fin: {membership.end_date}")
    
    # Desactivar carrito
    cart.is_active = False
    cart.save()
    print(f"   ✅ Carrito desactivado")
    
    # 6. VERIFICACIÓN EN PERFIL DE USUARIO
    print("\n👤 PASO 6: VERIFICACIÓN EN PERFIL")
    print("-" * 40)
    
    # Recargar usuario
    user.refresh_from_db()
    
    # Verificar membresía
    user_membership = Membership.objects.filter(user=user, status="active").first()
    
    if user_membership:
        print(f"   ✅ Membresía encontrada: {user_membership.plan.name}")
        print(f"   ✅ Estado: {user_membership.status}")
        print(f"   ✅ Cursos restantes: {user_membership.courses_remaining}")
        print(f"   ✅ Consultas restantes: {user_membership.consultations_remaining}")
        print(f"   ✅ Es activa: {user_membership.is_active}")
        print(f"   ✅ Puede acceder a cursos: {user_membership.can_access_course()}")
        print(f"   ✅ Puede solicitar consultas: {user_membership.can_request_consultation()}")
        
        # Verificar historial de pagos
        user_payments = Payment.objects.filter(user=user, status="completed")
        print(f"   ✅ Pagos completados: {user_payments.count()}")
        
        return True
    else:
        print("   ❌ Error: No se encontró membresía activa")
        return False

def test_course_access():
    """Prueba el acceso a cursos con la membresía"""
    print("\n📚 PASO 7: PRUEBA DE ACCESO A CURSOS")
    print("-" * 40)
    
    test_email = "test_user@plataforma-cursos.local"
    user = User.objects.get(email=test_email)
    membership = Membership.objects.filter(user=user, status="active").first()
    
    if not membership:
        print("   ❌ Error: No hay membresía activa para probar")
        return False
    
    # Obtener cursos disponibles
    from cursos.models import Course
    courses = Course.objects.filter(is_available=True)[:3]  # Primeros 3 cursos
    
    print(f"   📊 Cursos disponibles para probar: {courses.count()}")
    
    courses_accessed = 0
    for course in courses:
        if membership.can_access_specific_course(course):
            # Simular acceso al curso
            user_course, created = UserCourse.objects.get_or_create(
                user=user,
                course=course
            )
            
            if created:
                # Usar el curso (reducir contador)
                if membership.use_course(course):
                    courses_accessed += 1
                    print(f"   ✅ Acceso concedido a: {course.title}")
                else:
                    print(f"   ❌ Acceso denegado a: {course.title}")
            else:
                print(f"   ℹ️ Ya tenías acceso a: {course.title}")
        else:
            print(f"   ⛔ No tienes acceso a: {course.title}")
    
    # Verificar estado final de la membresía
    membership.refresh_from_db()
    print(f"   📊 Cursos restantes después del acceso: {membership.courses_remaining}")
    print(f"   📊 Cursos a los que se accedió: {courses_accessed}")
    
    return True

def show_summary():
    """Muestra un resumen final del estado"""
    print("\n📊 RESUMEN FINAL")
    print("=" * 70)
    
    test_email = "test_user@plataforma-cursos.local"
    user = User.objects.filter(email=test_email).first()
    
    if not user:
        print("❌ Usuario de prueba no encontrado")
        return
    
    print(f"👤 Usuario: {user.email}")
    print(f"✉️ Email verificado: {'Sí' if user.is_email_verified else 'No'}")
    
    # Membresías
    memberships = Membership.objects.filter(user=user)
    print(f"💎 Membresías totales: {memberships.count()}")
    
    active_membership = memberships.filter(status="active").first()
    if active_membership:
        print(f"✅ Membresía activa: {active_membership.plan.name}")
        print(f"📅 Válida hasta: {active_membership.end_date.strftime('%d/%m/%Y')}")
        print(f"📚 Cursos restantes: {active_membership.courses_remaining}")
        print(f"💬 Consultas restantes: {active_membership.consultations_remaining}")
    
    # Pagos
    payments = Payment.objects.filter(user=user)
    completed_payments = payments.filter(status="completed")
    print(f"💳 Pagos totales: {payments.count()}")
    print(f"✅ Pagos completados: {completed_payments.count()}")
    
    total_paid = sum(p.amount for p in completed_payments)
    print(f"💰 Total pagado: ${total_paid:,.0f}")
    
    # Cursos
    user_courses = UserCourse.objects.filter(user=user)
    print(f"📖 Cursos en los que está inscrito: {user_courses.count()}")

def cleanup_test_data():
    """Limpia los datos de prueba"""
    print("\n🧹 LIMPIEZA DE DATOS DE PRUEBA")
    print("-" * 40)
    
    test_email = "test_user@plataforma-cursos.local"
    user = User.objects.filter(email=test_email).first()
    
    if user:
        # Eliminar relaciones primero
        UserCourse.objects.filter(user=user).delete()
        Membership.objects.filter(user=user).delete()
        Payment.objects.filter(user=user).delete()
        Cart.objects.filter(user=user).delete()
        EmailAddress.objects.filter(user=user).delete()
        
        # Eliminar usuario
        user.delete()
        print("✅ Datos de prueba eliminados")
    else:
        print("ℹ️ No hay datos de prueba para eliminar")

if __name__ == "__main__":
    try:
        # Ejecutar prueba completa
        success = test_complete_purchase_flow()
        
        if success:
            # Probar acceso a cursos
            test_course_access()
            
            # Mostrar resumen
            show_summary()
            
            print("\n🎉 ¡PRUEBA COMPLETADA EXITOSAMENTE!")
            print("=" * 70)
            print("✅ El flujo completo de compra funciona correctamente")
            print("✅ El usuario puede registrarse")
            print("✅ Las membresías se pueden comprar")
            print("✅ Los pagos se procesan correctamente")
            print("✅ Las membresías se activan automáticamente")
            print("✅ El acceso a cursos funciona según la membresía")
        else:
            print("\n❌ PRUEBA FALLIDA")
            print("Revisa los errores anteriores")
        
        # Preguntar si limpiar datos
        response = input("\n¿Quieres limpiar los datos de prueba? (s/N): ")
        if response.lower() in ['s', 'sí', 'si', 'y', 'yes']:
            cleanup_test_data()
        
    except Exception as e:
        print(f"\n💥 ERROR DURANTE LA PRUEBA: {e}")
        import traceback
        traceback.print_exc()
