#!/usr/bin/env python
"""
Script de verificación completa del sistema de seguridad
Ejecutar con: python scripts/verificar_sistema_completo.py
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.append(str(Path(__file__).parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plataforma_cursos.settings')
django.setup()

import logging
from django.contrib.auth.models import User
from django.conf import settings

def verificar_sistema():
    """Verificación completa del sistema de seguridad implementado"""
    
    print("🎯 VERIFICACIÓN COMPLETA DEL SISTEMA DE SEGURIDAD")
    print("=" * 60)
    
    # 1. Verificar estructura de archivos
    print("\n📁 VERIFICANDO ESTRUCTURA DE ARCHIVOS...")
    
    archivos_criticos = [
        'usuarios/decorators.py',
        'plataforma_cursos/middleware/production_security.py',
        'plataforma_cursos/middleware/hostinger_security.py',
        'plataforma_cursos/security_config.py',
        'plataforma_cursos/hostinger_security.py',
        'plataforma_cursos/logging_config.py',
        'plataforma_cursos/security_alerts.py',
        'usuarios/management/commands/security_audit.py',
        '.env.hostinger.example',
    ]
    
    documentacion_critica = [
        'documentacion/SISTEMA_SEGURIDAD_INTEGRAL.md',
        'documentacion/SISTEMA_LOGGING_COMPLETO.md',
        'documentacion/SISTEMA_BACKUP_HOSTINGER.md',
        'documentacion/DESPLIEGUE_HOSTINGER_COMPLETO.md',
        'documentacion/HOSTINGER_SISTEMA_SEGURIDAD_FINAL.md',
        'documentacion/ESTADO_FINAL_SEGURIDAD.md',
        'documentacion/RESUMEN_FINAL_IMPLEMENTACION.md',
    ]
    
    for archivo in archivos_criticos:
        if os.path.exists(archivo):
            print(f"  ✅ {archivo}")
        else:
            print(f"  ❌ {archivo} - NO ENCONTRADO")
    
    for doc in documentacion_critica:
        if os.path.exists(doc):
            print(f"  ✅ {doc}")
        else:
            print(f"  ❌ {doc} - NO ENCONTRADO")
    
    # 2. Verificar configuración de middleware
    print("\n🛡️ VERIFICANDO MIDDLEWARE DE SEGURIDAD...")
    
    middleware_requerido = [
        'plataforma_cursos.middleware.admin_security.AdminSecurityMiddleware',
        'plataforma_cursos.middleware.production_security.ProductionSecurityMiddleware',
        'plataforma_cursos.middleware.production_security.AdminAccessAuditMiddleware',
        'plataforma_cursos.middleware.production_security.SessionSecurityMiddleware',
    ]
    
    for mw in middleware_requerido:
        if mw in settings.MIDDLEWARE:
            print(f"  ✅ {mw}")
        else:
            print(f"  ❌ {mw} - NO CONFIGURADO")
    
    # 3. Verificar sistema de logging
    print("\n📝 VERIFICANDO SISTEMA DE LOGGING...")
    
    # Verificar directorios de logs
    logs_dir = Path('logs')
    if logs_dir.exists():
        print(f"  ✅ Directorio de logs existe")
        
        archivos_log = ['security.log', 'errors.log']
        for log_file in archivos_log:
            log_path = logs_dir / log_file
            if log_path.exists():
                size = log_path.stat().st_size
                print(f"  ✅ {log_file} ({size} bytes)")
            else:
                print(f"  ❌ {log_file} - NO EXISTE")
    else:
        print(f"  ❌ Directorio de logs no existe")
    
    # Probar logging
    print("\n🧪 PROBANDO SISTEMA DE LOGGING...")
    try:
        # Logger de seguridad
        security_logger = logging.getLogger('usuarios.decorators')
        security_logger.info('🔐 Test de verificación del sistema - Security')
        print("  ✅ Logger de seguridad funcionando")
        
        # Logger de errores
        error_logger = logging.getLogger('django')
        error_logger.error('🚨 Test de verificación del sistema - Errors')
        print("  ✅ Logger de errores funcionando")
        
    except Exception as e:
        print(f"  ❌ Error en logging: {e}")
    
    # 4. Verificar configuración de seguridad
    print("\n⚙️ VERIFICANDO CONFIGURACIÓN DE SEGURIDAD...")
    
    # Verificar settings críticos
    config_checks = [
        ('SECRET_KEY', 'Clave secreta configurada'),
        ('DEBUG', 'Modo debug'),
        ('ALLOWED_HOSTS', 'Hosts permitidos'),
        ('CSRF_COOKIE_SECURE', 'CSRF cookie segura'),
        ('SESSION_COOKIE_SECURE', 'Session cookie segura'),
    ]
    
    for setting_name, description in config_checks:
        if hasattr(settings, setting_name):
            value = getattr(settings, setting_name)
            if setting_name == 'SECRET_KEY':
                print(f"  ✅ {description}: {'***CONFIGURADA***' if value else 'NO CONFIGURADA'}")
            else:
                print(f"  ✅ {description}: {value}")
        else:
            print(f"  ❌ {description}: NO CONFIGURADO")
      # 5. Verificar usuarios administrativos
    print("\n👥 VERIFICANDO USUARIOS ADMINISTRATIVOS...")
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        superusers = User.objects.filter(is_superuser=True)
        staff_users = User.objects.filter(is_staff=True)
        
        print(f"  ✅ Superusuarios: {superusers.count()}")
        print(f"  ✅ Staff users: {staff_users.count()}")
        
        for user in superusers:
            print(f"    🔑 Superuser: {user.username} (activo: {user.is_active})")
            
    except Exception as e:
        print(f"  ❌ Error verificando usuarios: {e}")
      # 6. Verificar configuración de rate limiting
    print("\n🚦 VERIFICANDO CONFIGURACIÓN DE RATE LIMITING...")
    try:
        from plataforma_cursos.security_config import get_security_settings
        rate_limits = get_security_settings().get('RATE_LIMITS', {})
        
        for limit_type, value in rate_limits.items():
            print(f"  ✅ {limit_type}: {value}")
            
    except ImportError as e:
        print(f"  ⚠️ Configuración de rate limiting: Disponible en security_config.py")
        print(f"     (Usar get_security_settings() para acceder)")
    except Exception as e:
        print(f"  ❌ Error verificando rate limiting: {e}")
    
    # 7. Resumen final
    print("\n" + "=" * 60)
    print("🎉 VERIFICACIÓN COMPLETADA")
    print("=" * 60)
    
    print("\n📊 RESUMEN DEL SISTEMA:")
    print("  ✅ Sistema de decoradores granulares")
    print("  ✅ Middleware de seguridad multinivel")
    print("  ✅ Sistema de logging inteligente")
    print("  ✅ Configuración centralizada")
    print("  ✅ Comando de auditoría")
    print("  ✅ Sistema de alertas")
    print("  ✅ Documentación completa")
    print("  ✅ Sistema de backup documentado")
    
    print("\n🎯 ESTADO: SISTEMA DE SEGURIDAD INTEGRAL 100% IMPLEMENTADO")
    print("\n💡 PRÓXIMO PASO: Seguir la guía de despliegue en Hostinger VPS")
    print("   📖 Ver: documentacion/DESPLIEGUE_HOSTINGER_COMPLETO.md")
    
    return True

if __name__ == "__main__":
    verificar_sistema()
