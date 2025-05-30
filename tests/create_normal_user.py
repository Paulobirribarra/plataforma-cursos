#!/usr/bin/env python
"""
Script para crear un usuario de prueba sin privilegios de staff
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plataforma_cursos.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_normal_user():
    """Crear un usuario normal sin privilegios de staff."""
    
    print("👤 CREANDO USUARIO DE PRUEBA SIN PRIVILEGIOS DE STAFF")
    print("="*55)
    
    # Datos del usuario de prueba
    email = "usuario_normal@test.com"
    password = "TestPassword123!"
    
    try:
        # Verificar si el usuario ya existe
        user = User.objects.get(email=email)
        print(f"⚠️ Usuario ya existe: {email}")
        
        # Asegurar que no tenga privilegios de staff
        user.is_staff = False
        user.is_superuser = False
        user.save()
        print(f"✅ Privilegios actualizados: is_staff={user.is_staff}, is_superuser={user.is_superuser}")
        
    except User.DoesNotExist:
        # Crear nuevo usuario
        user = User.objects.create_user(
            email=email,
            password=password,
            is_staff=False,
            is_superuser=False
        )
        print(f"✅ Usuario creado exitosamente: {email}")
        print(f"   - Password: {password}")
        print(f"   - is_staff: {user.is_staff}")
        print(f"   - is_superuser: {user.is_superuser}")
    
    print(f"\n📋 DATOS DE ACCESO:")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    print(f"   URL de login: http://127.0.0.1:8000/accounts/login/")
    
    print(f"\n✅ Usuario listo para pruebas")

if __name__ == "__main__":
    create_normal_user()
