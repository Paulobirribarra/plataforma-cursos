"""
Configuración de seguridad para entorno de producción
Este archivo contiene todas las configuraciones de seguridad recomendadas
"""
import os
from decouple import config

# =============================================================================
# CONFIGURACIÓN DE SEGURIDAD BÁSICA
# =============================================================================

# URL secreta para el panel de administración (cambiar en producción)
ADMIN_URL_SECRET = config('ADMIN_URL_SECRET', default='secret-admin-panel')

# Hosts permitidos (CRÍTICO: configurar correctamente en producción)
PRODUCTION_ALLOWED_HOSTS = [
    'tu-dominio.com',
    'www.tu-dominio.com',
    # Agregar todos los dominios reales aquí
]

# =============================================================================
# CONFIGURACIÓN DE RATE LIMITING
# =============================================================================

# Habilitar/deshabilitar rate limiting
ENABLE_RATE_LIMITING = config('ENABLE_RATE_LIMITING', default=True, cast=bool)

# Configuración de límites de rate limiting
RATE_LIMITING_CONFIG = {
    'login': {
        'requests': config('RATE_LIMIT_LOGIN_REQUESTS', default=5, cast=int),
        'window': config('RATE_LIMIT_LOGIN_WINDOW', default=300, cast=int),  # 5 minutos
    },
    'admin': {
        'requests': config('RATE_LIMIT_ADMIN_REQUESTS', default=50, cast=int),
        'window': config('RATE_LIMIT_ADMIN_WINDOW', default=300, cast=int),  # 5 minutos
    },
    'api': {
        'requests': config('RATE_LIMIT_API_REQUESTS', default=100, cast=int),
        'window': config('RATE_LIMIT_API_WINDOW', default=300, cast=int),  # 5 minutos
    },
    'general': {
        'requests': config('RATE_LIMIT_GENERAL_REQUESTS', default=200, cast=int),
        'window': config('RATE_LIMIT_GENERAL_WINDOW', default=300, cast=int),  # 5 minutos
    }
}

# =============================================================================
# CONFIGURACIÓN DE SESIONES SEGURAS
# =============================================================================

# Configuración de sesiones para producción
PRODUCTION_SESSION_CONFIG = {
    'SESSION_COOKIE_SECURE': True,  # Solo HTTPS
    'SESSION_COOKIE_HTTPONLY': True,  # No accesible desde JavaScript
    'SESSION_COOKIE_SAMESITE': 'Lax',  # Protección CSRF
    'SESSION_COOKIE_AGE': 3600,  # 1 hora para usuarios normales
    'SESSION_EXPIRE_AT_BROWSER_CLOSE': True,
    
    # Configuración específica para administradores
    'ADMIN_SESSION_TIMEOUT': 1800,  # 30 minutos para admins
    'ADMIN_REQUIRE_RECENT_LOGIN': True,  # Requerir login reciente para acciones críticas
}

# =============================================================================
# CONFIGURACIÓN DE CSRF
# =============================================================================

PRODUCTION_CSRF_CONFIG = {
    'CSRF_COOKIE_SECURE': True,  # Solo HTTPS
    'CSRF_COOKIE_HTTPONLY': True,  # No accesible desde JavaScript
    'CSRF_COOKIE_SAMESITE': 'Lax',
    'CSRF_USE_SESSIONS': False,  # Usar cookies en lugar de sesiones
    'CSRF_TRUSTED_ORIGINS': [
        'https://tu-dominio.com',
        'https://www.tu-dominio.com',
        # Agregar dominios de confianza aquí
    ]
}

# =============================================================================
# CONFIGURACIÓN DE HEADERS DE SEGURIDAD
# =============================================================================

SECURITY_HEADERS_CONFIG = {
    # Content Security Policy
    'CSP_DEFAULT_SRC': "'self'",
    'CSP_SCRIPT_SRC': "'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com",
    'CSP_STYLE_SRC': "'self' 'unsafe-inline' https://cdnjs.cloudflare.com",
    'CSP_IMG_SRC': "'self' data: https:",
    'CSP_FONT_SRC': "'self' https://cdnjs.cloudflare.com",
    'CSP_CONNECT_SRC': "'self'",
    'CSP_FRAME_SRC': "'none'",
    'CSP_OBJECT_SRC': "'none'",
    
    # Otros headers de seguridad
    'SECURE_BROWSER_XSS_FILTER': True,
    'SECURE_CONTENT_TYPE_NOSNIFF': True,
    'SECURE_HSTS_SECONDS': 31536000,  # 1 año
    'SECURE_HSTS_INCLUDE_SUBDOMAINS': True,
    'SECURE_HSTS_PRELOAD': True,
    'SECURE_FRAME_DENY': True,
}

# =============================================================================
# CONFIGURACIÓN DE LOGGING DE SEGURIDAD
# =============================================================================

SECURITY_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'security': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
        'detailed': {
            'format': '[{asctime}] {levelname} {name} {funcName}:{lineno}: {message}',
            'style': '{',
        }
    },
    'handlers': {
        'security_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(config('LOG_DIR', default='logs'), 'security.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'security',
        },
        'admin_access_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(config('LOG_DIR', default='logs'), 'admin_access.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'detailed',
        },
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'security',
        }
    },
    'loggers': {
        'usuarios.decorators': {
            'handlers': ['security_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'plataforma_cursos.middleware.production_security': {
            'handlers': ['security_file', 'admin_access_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'plataforma_cursos.middleware.admin_security': {
            'handlers': ['admin_access_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        }
    }
}

# =============================================================================
# CONFIGURACIÓN DE BACKUP Y AUDITORÍA
# =============================================================================

BACKUP_CONFIG = {
    'ENABLE_AUTO_BACKUP': config('ENABLE_AUTO_BACKUP', default=True, cast=bool),
    'BACKUP_FREQUENCY_HOURS': config('BACKUP_FREQUENCY_HOURS', default=24, cast=int),
    'BACKUP_RETENTION_DAYS': config('BACKUP_RETENTION_DAYS', default=30, cast=int),
    'BACKUP_LOCATION': config('BACKUP_LOCATION', default='backups/'),
    
    # Backup de logs de seguridad
    'BACKUP_SECURITY_LOGS': True,
    'SECURITY_LOG_RETENTION_DAYS': 90,
}

# =============================================================================
# CONFIGURACIÓN DE NOTIFICACIONES DE SEGURIDAD
# =============================================================================

SECURITY_NOTIFICATIONS_CONFIG = {
    'ENABLE_EMAIL_ALERTS': config('ENABLE_SECURITY_EMAIL_ALERTS', default=True, cast=bool),
    'ADMIN_EMAIL_ALERTS': [
        config('ADMIN_EMAIL', default='admin@tu-dominio.com'),
        # Agregar más emails de administradores aquí
    ],
    
    # Tipos de eventos que requieren notificación inmediata
    'CRITICAL_EVENTS': [
        'RATE_LIMIT_EXCEEDED',
        'SUSPICIOUS_ADMIN_ACTIVITY',
        'BLOCKED_IP_ACCESS_ATTEMPT',
        'ADMIN_SESSION_TIMEOUT',
        'SESSION_IP_CHANGE_ADMIN',
        'SUPERUSER_ACCESS',
    ],
    
    # Configuración de Slack (opcional)
    'SLACK_WEBHOOK_URL': config('SLACK_WEBHOOK_URL', default=''),
    'ENABLE_SLACK_ALERTS': config('ENABLE_SLACK_ALERTS', default=False, cast=bool),
}

# =============================================================================
# CONFIGURACIÓN DE BASE DE DATOS SEGURA
# =============================================================================

DATABASE_SECURITY_CONFIG = {
    'CONN_MAX_AGE': 0,  # No reutilizar conexiones
    'ATOMIC_REQUESTS': True,  # Transacciones automáticas
    'OPTIONS': {
        'isolation_level': None,  # Usar el nivel de aislamiento por defecto
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",  # Para MySQL
    }
}

# =============================================================================
# CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS SEGUROS
# =============================================================================

STATIC_SECURITY_CONFIG = {
    'STATIC_URL': '/static/',
    'MEDIA_URL': '/media/',
    
    # En producción, servir archivos estáticos con nginx/apache
    'SERVE_STATIC_FILES': False,
    
    # Configuración de CORS para archivos estáticos
    'STATIC_CORS_ALLOWED_ORIGINS': [
        'https://tu-dominio.com',
        'https://www.tu-dominio.com',
    ]
}

# =============================================================================
# FUNCIONES DE AYUDA PARA APLICAR CONFIGURACIONES
# =============================================================================

def apply_production_security_settings(settings_dict):
    """
    Aplicar configuraciones de seguridad a settings de Django
    """
    # Solo aplicar en producción (cuando DEBUG=False)
    if not settings_dict.get('DEBUG', True):
        
        # Aplicar configuración de sesiones
        settings_dict.update(PRODUCTION_SESSION_CONFIG)
        
        # Aplicar configuración de CSRF
        settings_dict.update(PRODUCTION_CSRF_CONFIG)
        
        # Aplicar headers de seguridad
        settings_dict.update(SECURITY_HEADERS_CONFIG)
        
        # Configurar hosts permitidos
        settings_dict['ALLOWED_HOSTS'] = PRODUCTION_ALLOWED_HOSTS
        
        # Configurar logging de seguridad
        settings_dict['LOGGING'] = SECURITY_LOGGING_CONFIG
        
        # Forzar HTTPS
        settings_dict['SECURE_SSL_REDIRECT'] = True
        settings_dict['SECURE_PROXY_SSL_HEADER'] = ('HTTP_X_FORWARDED_PROTO', 'https')
        
        print("✅ Configuraciones de seguridad de producción aplicadas")
    else:
        print("⚠️ Modo desarrollo detectado - Configuraciones de seguridad limitadas")

def get_admin_url():
    """Obtener URL secreta del admin"""
    return f"/{ADMIN_URL_SECRET}/"

def validate_security_config():
    """Validar configuración de seguridad"""
    errors = []
    
    # Verificar que se hayan configurado variables críticas
    if ADMIN_URL_SECRET == 'secret-admin-panel':
        errors.append("⚠️ ADMIN_URL_SECRET debe cambiarse en producción")
    
    if not config('SECRET_KEY', default='').startswith('django-insecure'):
        if len(config('SECRET_KEY', default='')) < 50:
            errors.append("⚠️ SECRET_KEY debe ser más larga y aleatoria")
    
    # Verificar hosts permitidos
    if 'tu-dominio.com' in PRODUCTION_ALLOWED_HOSTS:
        errors.append("⚠️ PRODUCTION_ALLOWED_HOSTS debe configurarse con dominios reales")
    
    if errors:
        print("🚨 Errores de configuración de seguridad:")
        for error in errors:
            print(f"  {error}")
    else:
        print("✅ Configuración de seguridad validada correctamente")
    
    return len(errors) == 0
