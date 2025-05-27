#!/usr/bin/env python
"""
Script para verificar el email del superusuario existente
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plataforma_cursos.settings')
django.setup()

from usuarios.models import CustomUser

def verify_superuser_email():
    """Marca como verificado el email del superusuario admin@example.com"""
    try:
        # Buscar al superusuario
        superuser = CustomUser.objects.get(email='admin@example.com', is_superuser=True)
        
        # Verificar su email
        superuser.is_email_verified = True
        superuser.email_verification_token = None
        superuser.failed_login_attempts = 0
        superuser.account_locked_until = None
        superuser.save()
        
        print(f"✅ Email verificado para el superusuario: {superuser.email}")
        print(f"   - is_email_verified: {superuser.is_email_verified}")
        print(f"   - is_active: {superuser.is_active}")
        print(f"   - is_staff: {superuser.is_staff}")
        print(f"   - is_superuser: {superuser.is_superuser}")
        
    except CustomUser.DoesNotExist:
        print("❌ No se encontró el superusuario admin@example.com")
        print("\nSuperusuarios existentes:")
        for user in CustomUser.objects.filter(is_superuser=True):
            print(f"   - {user.email} (verificado: {user.is_email_verified})")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    verify_superuser_email()
