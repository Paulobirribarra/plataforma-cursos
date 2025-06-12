from decouple import config
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", cast=bool)

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']  # Temporalmente para desarrollo/compartir

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",  # Requerido por Allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",    "usuarios.apps.UsuariosConfig",
    "cursos.apps.CursosConfig",
    "pagos.apps.PagosConfig",
    "membresias.apps.MembresiasConfig",
    "blogs.apps.BlogsConfig",  # App para contacto y blogs
    "boletines.apps.BoletinesConfig",  # App para boletines informativos
    "widget_tweaks",
    "carrito",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    # Middleware de seguridad integral
    "plataforma_cursos.middleware.admin_security.AdminSecurityMiddleware",
    "plataforma_cursos.middleware.admin_security.AdminSessionSecurityMiddleware",
    "plataforma_cursos.middleware.production_security.ProductionSecurityMiddleware",
    "plataforma_cursos.middleware.production_security.AdminAccessAuditMiddleware",
    "plataforma_cursos.middleware.production_security.SessionSecurityMiddleware",
]

ROOT_URLCONF = "plataforma_cursos.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "plataforma_cursos.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT"),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "usuarios.CustomUser"

# Internationalization
LANGUAGE_CODE = "es"

TIME_ZONE = "America/Santiago"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files (archivos subidos por usuarios)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Configuración de Allauth
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
SITE_ID = 1
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "username", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

# Configuración de formularios personalizados para allauth
ACCOUNT_FORMS = {
    'signup': 'usuarios.forms.CustomUserCreationForm',
}
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_SIGNUP_REDIRECT_URL = "/usuarios/dashboard/"
LOGIN_REDIRECT_URL = "/usuarios/dashboard/"
LOGIN_URL = "/accounts/login/"  
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = "/accounts/login/"  
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = "/usuarios/dashboard/"

# Configuración de correo (SMTP GMAIL - ACTIVO)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('EMAIL_HOST_USER')  # Usar tu email de Gmail
CONTACT_EMAIL = config('CONTACT_EMAIL', default='contact@yoursite.com')  # Email donde recibirás las consultas

# Configuración de codificación para emails
DEFAULT_CHARSET = 'utf-8'
FILE_CHARSET = 'utf-8'

# Configuración para priorizar emails HTML
EMAIL_USE_LOCALTIME = True
EMAIL_SUBJECT_PREFIX = ''

# Configuración de allauth para formato de email
ACCOUNT_EMAIL_SUBJECT_PREFIX = ''
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https' if DEBUG == False else 'http'

# Configuración de correo (para pruebas en consola - DESACTIVADO)
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CSRF_COOKIE_SECURE = (
    False  # En desarrollo, debería ser False (True solo en producción con HTTPS)
)
SESSION_COOKIE_SECURE = False  # Igual que CSRF_COOKIE_SECURE

# Configuración para ngrok y dominios externos
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://*.ngrok-free.app',  # Para ngrok
    'https://*.ngrok.io',        # Para versiones anteriores de ngrok
    'https://*.ngrok.app',       # Para versiones más recientes de ngrok
    'https://6ba4-179-57-9-30.ngrok-free.app',  # URL específica actual de ngrok
]

# Configuración básica de logging
# La configuración completa se maneja en logging_config.py

# =============================================================================
# CONFIGURACIÓN DE SEGURIDAD INTEGRAL Y LOGGING
# =============================================================================

# Configuración de rate limiting
ENABLE_RATE_LIMITING = config('ENABLE_RATE_LIMITING', default=True, cast=bool)

# URL secreta para el panel de administración
ADMIN_URL_SECRET = config('ADMIN_URL_SECRET', default='secret-admin-panel')

# Configuración de seguridad para producción
if not DEBUG:
    # Headers de seguridad
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_FRAME_DENY = True
    
    # Configuración de cookies seguras
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SAMESITE = 'Lax'
    
    # Forzar HTTPS
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Configuración de sesiones administrativas
ADMIN_SESSION_TIMEOUT = 1800  # 30 minutos para admins

# Configurar logging inteligente según el ambiente
if not DEBUG:
    # Configuración de producción - Optimizada para bajo tráfico
    from plataforma_cursos.logging_config import setup_production_logging
    LOGGING = setup_production_logging(low_traffic=True)
else:
    # Configuración de desarrollo - Optimizada y simplificada
    from plataforma_cursos.logging_config import setup_development_logging
    LOGGING = setup_development_logging()
