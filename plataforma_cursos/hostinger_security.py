"""
Configuración de seguridad optimizada para Hostinger VPS
Aprovecha el acceso SSH completo y configuración de servidor
"""
import os
from decouple import config

def configure_hostinger_security():
    """
    Configuración específica para Hostinger VPS
    """
    
    # Configuración de servidor web (Nginx/Apache)
    HOSTINGER_SECURITY = {
        'server_type': 'VPS',  # VPS, Cloud, o Shared
        'has_ssh_access': True,
        'can_configure_firewall': True,
        'has_root_access': True,
        'ssl_available': True,
    }
    
    # Headers de seguridad que SÍ puedes configurar en Hostinger
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
        'Content-Security-Policy': (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        ),
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
    }
    
    # Rate limiting más agresivo (aprovechando recursos del VPS)
    HOSTINGER_RATE_LIMITS = {
        'login': {'requests': 3, 'window': 300, 'block_duration': 900},  # 3 intentos, bloqueo 15min
        'admin': {'requests': 30, 'window': 300, 'block_duration': 300}, # 30 requests, bloqueo 5min
        'api': {'requests': 200, 'window': 300, 'block_duration': 60},   # 200 requests, bloqueo 1min
        'general': {'requests': 500, 'window': 300, 'block_duration': 30}, # 500 requests generales
    }
    
    # Configuración de firewall (UFW en Ubuntu)
    FIREWALL_RULES = {
        'ssh_port': config('SSH_PORT', default=22, cast=int),
        'allowed_ips': config('ALLOWED_IPS', default='').split(','),
        'block_countries': config('BLOCK_COUNTRIES', default='').split(','),
        'enable_fail2ban': config('ENABLE_FAIL2BAN', default=True, cast=bool),
    }
    
    # Configuración de base de datos segura
    DATABASE_SECURITY = {
        'host': '127.0.0.1',  # Solo conexiones locales
        'port': config('DB_PORT', default=3306, cast=int),
        'ssl_mode': 'REQUIRED',
        'charset': 'utf8mb4',
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        'options': {
            'autocommit': True,
        }
    }
    
    return {
        'hostinger_config': HOSTINGER_SECURITY,
        'security_headers': SECURITY_HEADERS,
        'rate_limits': HOSTINGER_RATE_LIMITS,
        'firewall': FIREWALL_RULES,
        'database': DATABASE_SECURITY,
    }

def get_hostinger_middleware():
    """
    Middleware específico para Hostinger VPS
    """
    return [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "allauth.account.middleware.AccountMiddleware",
        
        # Middleware de seguridad integral para VPS
        "plataforma_cursos.middleware.admin_security.AdminSecurityMiddleware",
        "plataforma_cursos.middleware.hostinger_security.HostingerVPSSecurityMiddleware",
        "plataforma_cursos.middleware.hostinger_security.HostingerRateLimitMiddleware",
        "plataforma_cursos.middleware.hostinger_security.HostingerFirewallMiddleware",
    ]

def apply_hostinger_settings(settings_dict):
    """
    Aplicar configuraciones específicas de Hostinger
    """
    config = configure_hostinger_security()
    
    # Configuración de seguridad HTTPS
    if not settings_dict.get('DEBUG', False):
        # Configuración SSL/HTTPS
        settings_dict.update({
            'SECURE_SSL_REDIRECT': True,
            'SECURE_PROXY_SSL_HEADER': ('HTTP_X_FORWARDED_PROTO', 'https'),
            'SECURE_BROWSER_XSS_FILTER': True,
            'SECURE_CONTENT_TYPE_NOSNIFF': True,
            'SECURE_HSTS_SECONDS': 31536000,  # 1 año
            'SECURE_HSTS_INCLUDE_SUBDOMAINS': True,
            'SECURE_HSTS_PRELOAD': True,
            'SECURE_FRAME_DENY': True,
            
            # Cookies seguras
            'SESSION_COOKIE_SECURE': True,
            'SESSION_COOKIE_HTTPONLY': True,
            'SESSION_COOKIE_SAMESITE': 'Strict',
            'CSRF_COOKIE_SECURE': True,
            'CSRF_COOKIE_HTTPONLY': True,
            'CSRF_COOKIE_SAMESITE': 'Strict',
        })
    
    # Configuración de base de datos segura
    if 'DATABASES' in settings_dict:
        settings_dict['DATABASES']['default'].update({
            'OPTIONS': config['database']['options'],
            'HOST': config['database']['host'],
        })
    
    # Headers de seguridad personalizados
    settings_dict['HOSTINGER_SECURITY_HEADERS'] = config['security_headers']
    settings_dict['HOSTINGER_RATE_LIMITS'] = config['rate_limits']
    
    return settings_dict

# Variables de entorno específicas para Hostinger
HOSTINGER_ENV_VARS = """
# === CONFIGURACIÓN HOSTINGER VPS ===

# Información del servidor
SERVER_TYPE=VPS
HOSTINGER_PANEL_URL=https://hpanel.hostinger.com

# SSH y acceso
SSH_PORT=22
SSH_KEY_PATH=/home/u123456789/.ssh/authorized_keys

# Base de datos (Hostinger proporciona estos datos)
DB_NAME=u123456789_plataforma
DB_USER=u123456789_django
DB_PASSWORD=tu_password_de_hostinger
DB_HOST=localhost
DB_PORT=3306

# SSL y dominio
DOMAIN_NAME=tu-dominio.com
SSL_ENABLED=True
CLOUDFLARE_ENABLED=False

# Seguridad avanzada
ENABLE_FAIL2BAN=True
ALLOWED_IPS=tu.ip.fija.aqui
BLOCK_COUNTRIES=CN,RU
ADMIN_IP_WHITELIST=tu.ip.admin.aqui

# Email SMTP (Hostinger proporciona)
EMAIL_HOST=smtp.hostinger.com
EMAIL_PORT=587
EMAIL_HOST_USER=admin@tu-dominio.com
EMAIL_HOST_PASSWORD=tu_password_email
EMAIL_USE_TLS=True

# Alertas de seguridad
SECURITY_EMAIL=seguridad@tu-dominio.com
ENABLE_SLACK_ALERTS=False
SLACK_WEBHOOK_URL=

# Rate limiting agresivo
RATE_LIMIT_LOGIN=3
RATE_LIMIT_ADMIN=30
RATE_LIMIT_API=200
RATE_LIMIT_GENERAL=500
"""
