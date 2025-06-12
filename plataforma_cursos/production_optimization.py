"""
Configuraciones de optimización para sitios de bajo a medio tráfico
Estas configuraciones ayudan a optimizar recursos y rendimiento
"""
from decouple import config

# Configuraciones de optimización para bajo tráfico
LOW_TRAFFIC_OPTIMIZATIONS = {
    # Rate limiting más permisivo para sitios pequeños
    'RATE_LIMITS': {
        'login_attempts': 10,  # 10 intentos en lugar de 5
        'admin_requests': 100,  # 100 requests en lugar de 50
        'api_requests': 200,   # 200 requests en lugar de 100
        'general_requests': 500,  # 500 requests generales
        'rate_window_minutes': 5,  # Ventana de 5 minutos
    },
    
    # Configuración de sesiones optimizada
    'SESSION_CONFIG': {
        'SESSION_COOKIE_AGE': 3600 * 6,  # 6 horas para usuarios normales
        'ADMIN_SESSION_TIMEOUT': 1800,   # 30 minutos para admins
        'SESSION_SAVE_EVERY_REQUEST': False,  # Solo guardar cuando cambie
        'SESSION_EXPIRE_AT_BROWSER_CLOSE': False,
    },
    
    # Configuración de caché simplificada
    'CACHE_CONFIG': {
        'CACHE_TIMEOUT': 300,  # 5 minutos de caché por defecto
        'STATIC_CACHE_TIMEOUT': 86400,  # 1 día para archivos estáticos
        'USER_CACHE_TIMEOUT': 600,  # 10 minutos para datos de usuario
    },
    
    # Configuración de base de datos
    'DATABASE_CONFIG': {
        'CONN_MAX_AGE': 300,  # 5 minutos de conexión persistente
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        }
    },
    
    # Configuración de archivos de log
    'LOG_CONFIG': {
        'MAX_FILE_SIZE_MB': 5,  # Archivos más pequeños
        'BACKUP_COUNT': 5,      # Menos archivos de backup
        'CLEANUP_DAYS': 30,     # Limpiar logs después de 30 días
        'CRITICAL_RETENTION_DAYS': 90,  # Críticos se mantienen 90 días
    }
}

# Configuraciones de optimización para medio tráfico
MEDIUM_TRAFFIC_OPTIMIZATIONS = {
    'RATE_LIMITS': {
        'login_attempts': 8,
        'admin_requests': 75,
        'api_requests': 150,
        'general_requests': 300,
        'rate_window_minutes': 5,
    },
    
    'SESSION_CONFIG': {
        'SESSION_COOKIE_AGE': 3600 * 4,  # 4 horas
        'ADMIN_SESSION_TIMEOUT': 1200,   # 20 minutos para admins
        'SESSION_SAVE_EVERY_REQUEST': False,
        'SESSION_EXPIRE_AT_BROWSER_CLOSE': False,
    },
    
    'CACHE_CONFIG': {
        'CACHE_TIMEOUT': 600,  # 10 minutos
        'STATIC_CACHE_TIMEOUT': 86400,
        'USER_CACHE_TIMEOUT': 300,
    },
    
    'DATABASE_CONFIG': {
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        }
    },
    
    'LOG_CONFIG': {
        'MAX_FILE_SIZE_MB': 10,
        'BACKUP_COUNT': 10,
        'CLEANUP_DAYS': 45,
        'CRITICAL_RETENTION_DAYS': 180,
    }
}

def get_optimization_config(traffic_level='low'):
    """
    Obtener configuración de optimización según el nivel de tráfico
    
    Args:
        traffic_level (str): 'low' o 'medium'
        
    Returns:
        dict: Configuraciones optimizadas
    """
    if traffic_level == 'medium':
        return MEDIUM_TRAFFIC_OPTIMIZATIONS
    return LOW_TRAFFIC_OPTIMIZATIONS

def apply_rate_limiting_config(settings_dict, traffic_level='low'):
    """
    Aplicar configuraciones de rate limiting al settings
    
    Args:
        settings_dict (dict): Diccionario de settings de Django
        traffic_level (str): Nivel de tráfico ('low' o 'medium')
    """
    config = get_optimization_config(traffic_level)
    rate_limits = config['RATE_LIMITS']
    
    # Aplicar configuraciones de rate limiting
    settings_dict.update({
        'RATE_LIMIT_LOGIN_ATTEMPTS': rate_limits['login_attempts'],
        'RATE_LIMIT_ADMIN_REQUESTS': rate_limits['admin_requests'], 
        'RATE_LIMIT_API_REQUESTS': rate_limits['api_requests'],
        'RATE_LIMIT_GENERAL_REQUESTS': rate_limits['general_requests'],
        'RATE_LIMIT_WINDOW_MINUTES': rate_limits['rate_window_minutes'],
    })

def apply_session_config(settings_dict, traffic_level='low'):
    """
    Aplicar configuraciones de sesión optimizadas
    """
    config = get_optimization_config(traffic_level)
    session_config = config['SESSION_CONFIG']
    
    settings_dict.update(session_config)

def apply_database_config(settings_dict, traffic_level='low'):
    """
    Aplicar configuraciones de base de datos optimizadas
    """
    config = get_optimization_config(traffic_level)
    db_config = config['DATABASE_CONFIG']
    
    # Aplicar a la base de datos por defecto
    if 'DATABASES' in settings_dict and 'default' in settings_dict['DATABASES']:
        settings_dict['DATABASES']['default'].update(db_config)

def get_monitoring_thresholds(traffic_level='low'):
    """
    Obtener umbrales de monitoreo según el nivel de tráfico
    
    Returns:
        dict: Umbrales para alertas y monitoreo
    """
    if traffic_level == 'low':
        return {
            'daily_unique_visitors_alert': 1000,
            'hourly_requests_alert': 500,
            'error_rate_threshold': 0.05,  # 5%
            'response_time_alert_ms': 2000,  # 2 segundos
            'disk_usage_alert_percent': 80,
            'memory_usage_alert_percent': 85,
        }
    else:  # medium traffic
        return {
            'daily_unique_visitors_alert': 5000,
            'hourly_requests_alert': 2000,
            'error_rate_threshold': 0.03,  # 3%
            'response_time_alert_ms': 1500,  # 1.5 segundos
            'disk_usage_alert_percent': 75,
            'memory_usage_alert_percent': 80,
        }

# Configuraciones específicas para hosting compartido
SHARED_HOSTING_CONFIG = {
    'RATE_LIMITS': {
        'login_attempts': 15,  # Más permisivo para evitar bloqueos
        'admin_requests': 200,
        'api_requests': 300,
        'general_requests': 1000,
        'rate_window_minutes': 10,  # Ventana más larga
    },
    
    'LOG_CONFIG': {
        'MAX_FILE_SIZE_MB': 2,  # Archivos muy pequeños
        'BACKUP_COUNT': 3,
        'CLEANUP_DAYS': 14,  # Limpieza más frecuente
        'CRITICAL_RETENTION_DAYS': 30,
    },
    
    'PERFORMANCE': {
        'USE_FILE_SESSIONS': True,  # Evitar DB para sesiones
        'DISABLE_MIGRATIONS_CHECK': True,  # Para reducir carga
        'SIMPLIFIED_LOGGING': True,  # Logging mínimo
    }
}

def apply_shared_hosting_optimizations(settings_dict):
    """
    Aplicar optimizaciones específicas para hosting compartido
    """
    config = SHARED_HOSTING_CONFIG
    
    # Rate limiting más permisivo
    rate_limits = config['RATE_LIMITS']
    settings_dict.update({
        'RATE_LIMIT_LOGIN_ATTEMPTS': rate_limits['login_attempts'],
        'RATE_LIMIT_ADMIN_REQUESTS': rate_limits['admin_requests'],
        'RATE_LIMIT_API_REQUESTS': rate_limits['api_requests'],
        'RATE_LIMIT_GENERAL_REQUESTS': rate_limits['general_requests'],
        'RATE_LIMIT_WINDOW_MINUTES': rate_limits['rate_window_minutes'],
    })
    
    # Optimizaciones de rendimiento
    perf_config = config['PERFORMANCE']
    if perf_config.get('USE_FILE_SESSIONS'):
        settings_dict['SESSION_ENGINE'] = 'django.contrib.sessions.backends.file'
        settings_dict['SESSION_FILE_PATH'] = '/tmp/django_sessions'
    
    return settings_dict
