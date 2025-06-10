#!/usr/bin/env python
"""
Script para verificar usuarios en la base de datos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plataforma_cursos.settings')
django.setup()

from usuarios.models import CustomUser

def main():
    print("🔍 VERIFICANDO USUARIOS EN LA BASE DE DATOS")
    print("=" * 50)
    
    # Contar usuarios
    total_users = CustomUser.objects.count()
    
    print(f"📊 Total de usuarios: {total_users}")
    
    if total_users > 0:
        print("\n👥 USUARIOS REGISTRADOS:")
        print("-" * 30)
        
        for user in CustomUser.objects.all()[:10]:  # Mostrar máximo 10
            status = []
            if user.is_superuser:
                status.append("SUPERUSER")
            if user.is_staff:
                status.append("STAFF")
            if user.is_active:
                status.append("ACTIVO")
            else:
                status.append("INACTIVO")
            
            status_str = " | ".join(status)
            
            print(f"• {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Estado: {status_str}")
            print(f"  Último login: {user.last_login}")
            print()
            
        if total_users > 10:
            print(f"... y {total_users - 10} usuarios más")
    else:
        print("\n❌ No hay usuarios registrados en la base de datos")
        print("\n💡 Para crear un superusuario ejecuta:")
        print("python manage.py createsuperuser")

if __name__ == "__main__":
    main()
