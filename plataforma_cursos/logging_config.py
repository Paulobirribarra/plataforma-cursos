"""
Sistema de logging inteligente para producción
Maneja rotación automática, limpieza y configuración optimizada para bajo/medio tráfico
"""
import os
import logging.config
from pathlib import Path
from decouple import config
from datetime import datetime

def setup_production_logging(low_traffic=True):
    """
    Configurar sistema de logging para producción
    
    Args:
        low_traffic (bool): Si True, optimiza para sitios de bajo tráfico
        
    Returns:
        dict: Configuración de logging lista para usar en settings.py
    """
    
    # Crear directorio de logs si no existe
    log_dir = Path(config('LOG_DIR', default='logs'))
    log_dir.mkdir(exist_ok=True)
    
    # Configuración de logging con rotación automática
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{asctime} [{levelname}] {name} {process:d} {thread:d}: {message}',
                'style': '{',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '{asctime} [{levelname}] {name}: {message}',
                'style': '{',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'security': {
                'format': '{asctime} [SECURITY] {levelname} {name}: {message}',
                'style': '{',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            
            # Logs de seguridad con rotación diaria (máximo 30 días)
            'security_file': {
                'level': 'INFO',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': log_dir / 'security.log',
                'when': 'midnight',
                'interval': 1,
                'backupCount': 30,  # Mantener 30 días
                'formatter': 'security',
                'encoding': 'utf-8'
            },
            
            # Accesos admin con rotación semanal (máximo 4 semanas)
            'admin_access_file': {
                'level': 'INFO',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': log_dir / 'admin_access.log',
                'when': 'W0',  # Lunes
                'interval': 1,
                'backupCount': 4,  # Mantener 4 semanas
                'formatter': 'verbose',
                'encoding': 'utf-8'
            },
            
            # Errores generales con rotación por tamaño (máximo 10 archivos de 5MB)
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': log_dir / 'errors.log',
                'maxBytes': 5 * 1024 * 1024,  # 5MB
                'backupCount': 10,
                'formatter': 'verbose',
                'encoding': 'utf-8'
            },
            
            # Logs de aplicación general con rotación diaria (máximo 7 días)
            'application_file': {
                'level': 'INFO',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': log_dir / 'application.log',
                'when': 'midnight',
                'interval': 1,
                'backupCount': 7,  # Solo 7 días para logs generales
                'formatter': 'simple',
                'encoding': 'utf-8'
            },
            
            # Logs críticos que nunca se eliminan (solo rotación por tamaño)
            'critical_file': {
                'level': 'CRITICAL',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': log_dir / 'critical.log',
                'maxBytes': 10 * 1024 * 1024,  # 10MB
                'backupCount': 50,  # Mantener muchos archivos críticos
                'formatter': 'verbose',
                'encoding': 'utf-8'
            }
        },
        'loggers': {
            # Logger principal de Django
            'django': {
                'handlers': ['console', 'application_file', 'error_file'],
                'level': 'INFO',
                'propagate': False,
            },
            
            # Loggers de seguridad
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
            },
            
            # Loggers de aplicaciones
            'boletines': {
                'handlers': ['application_file', 'error_file'],
                'level': 'INFO',
                'propagate': True,
            },
            'cursos': {
                'handlers': ['application_file', 'error_file'],
                'level': 'INFO',
                'propagate': True,
            },
            'pagos': {
                'handlers': ['application_file', 'error_file', 'critical_file'],
                'level': 'INFO',
                'propagate': True,
            },
            'membresias': {
                'handlers': ['application_file', 'error_file'],
                'level': 'INFO',
                'propagate': True,
            },
            
            # Logger raíz para capturar todo lo demás
            'root': {
                'handlers': ['console', 'application_file', 'error_file'],
                'level': 'WARNING',
            }
        }
    }
      # Ajustar configuración para bajo tráfico
    if low_traffic:
        # Reducir tamaños de archivo para sitios de bajo tráfico
        for handler_name, handler_config in LOGGING_CONFIG['handlers'].items():
            if 'maxBytes' in handler_config:
                # Reducir a la mitad los tamaños para bajo tráfico
                handler_config['maxBytes'] = handler_config['maxBytes'] // 2
            if 'backupCount' in handler_config:
                # Mantener menos archivos históricos
                if handler_name != 'critical_file':  # Críticos siempre mantienen muchos
                    handler_config['backupCount'] = max(5, handler_config['backupCount'] // 2)
    
    # Aplicar configuración
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Log de inicio del sistema
    logger = logging.getLogger('usuarios.decorators')
    logger.info(f"Sistema de logging iniciado en {datetime.now()}")
    
    return LOGGING_CONFIG

def get_log_statistics():
    """
    Obtener estadísticas de uso de logs
    """
    log_dir = Path(config('LOG_DIR', default='logs'))
    stats = {
        'total_files': 0,
        'total_size_mb': 0,
        'files_info': []
    }
    
    if log_dir.exists():
        for log_file in log_dir.glob('*.log*'):
            if log_file.is_file():
                size_bytes = log_file.stat().st_size
                size_mb = size_bytes / (1024 * 1024)
                
                stats['files_info'].append({
                    'name': log_file.name,
                    'size_mb': round(size_mb, 2),
                    'modified': datetime.fromtimestamp(log_file.stat().st_mtime)
                })
                
                stats['total_files'] += 1
                stats['total_size_mb'] += size_mb
    
    stats['total_size_mb'] = round(stats['total_size_mb'], 2)
    return stats

def cleanup_old_logs(days_to_keep=90):
    """
    Limpieza manual de logs antiguos (solo archivos de backup)
    """
    log_dir = Path(config('LOG_DIR', default='logs'))
    cleaned_files = []
    
    if not log_dir.exists():
        return cleaned_files
    
    from datetime import datetime, timedelta
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    
    # Solo eliminar archivos de backup (que contienen fechas)
    for log_file in log_dir.glob('*.log.*'):
        if log_file.is_file():
            # Verificar si es un archivo de backup por su patrón
            if any(char.isdigit() for char in log_file.suffix):
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff_date:
                    try:
                        log_file.unlink()
                        cleaned_files.append(log_file.name)
                    except Exception as e:
                        logger = logging.getLogger('usuarios.decorators')
                        logger.error(f"Error eliminando archivo de log {log_file}: {e}")
    
    return cleaned_files

class LogManager:
    """
    Gestor de logs para facilitar el uso
    """
    
    @staticmethod
    def log_security_event(user, event_type, details, request=None):
        """Log eventos de seguridad"""
        logger = logging.getLogger('usuarios.decorators')
        
        user_info = user.username if hasattr(user, 'username') and user.is_authenticated else 'Anonymous'
        ip = LogManager._get_client_ip(request) if request else 'Unknown'
        
        message = f"USER: {user_info} | IP: {ip} | EVENT: {event_type} | DETAILS: {details}"
        logger.warning(message)
    
    @staticmethod
    def log_admin_access(user, path, method, request=None):
        """Log accesos administrativos"""
        logger = logging.getLogger('plataforma_cursos.middleware.admin_security')
        
        ip = LogManager._get_client_ip(request) if request else 'Unknown'
        user_info = user.username if hasattr(user, 'username') and user.is_authenticated else 'Anonymous'
        
        message = f"ADMIN_ACCESS | USER: {user_info} | IP: {ip} | {method} {path}"
        logger.info(message)
    
    @staticmethod
    def log_application_event(app_name, event_type, details, level='info'):
        """Log eventos de aplicación"""
        logger = logging.getLogger(app_name)
        
        message = f"{event_type}: {details}"
        getattr(logger, level.lower())(message)
    
    @staticmethod
    def log_payment_event(event_type, details, level='info'):
        """Log eventos de pagos (críticos)"""
        logger = logging.getLogger('pagos')
        
        message = f"PAYMENT_{event_type}: {details}"
        getattr(logger, level.lower())(message)
    
    @staticmethod
    def _get_client_ip(request):
        """Obtener IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

# Configuración específica para entornos de bajo tráfico
LOW_TRAFFIC_LOGGING_CONFIG = {
    'retention_days': {
        'security': 30,      # Logs de seguridad: 30 días
        'admin': 30,         # Accesos admin: 30 días  
        'application': 7,    # Logs generales: 7 días
        'errors': 60,        # Errores: 60 días
        'critical': 365      # Críticos: 1 año
    },
    'max_file_size_mb': {
        'security': 10,      # Máximo 10MB por archivo
        'admin': 5,          # Máximo 5MB por archivo
        'application': 20,   # Máximo 20MB por archivo
        'errors': 10,        # Máximo 10MB por archivo
        'critical': 50       # Máximo 50MB por archivo
    },
    'total_storage_limit_mb': 500,  # Límite total: 500MB
}

def estimate_log_usage(daily_events_estimate):
    """
    Estimar uso de almacenamiento basado en eventos diarios
    """
    # Tamaño promedio por línea de log (en bytes)
    avg_line_size = 150
    
    # Cálculos de estimación
    daily_lines = daily_events_estimate
    daily_size_mb = (daily_lines * avg_line_size) / (1024 * 1024)
    
    # Estimación mensual considerando retención
    monthly_size_mb = daily_size_mb * 30  # 30 días de seguridad
    
    estimates = {
        'daily_events': daily_events_estimate,
        'daily_size_mb': round(daily_size_mb, 2),
        'monthly_size_mb': round(monthly_size_mb, 2),
        'yearly_size_mb': round(daily_size_mb * 365, 2),
        'storage_with_retention_mb': round(monthly_size_mb * 1.5, 2)  # Factor de seguridad
    }
    
    return estimates

def setup_development_logging():
    """
    Configuración de logging simplificada para desarrollo
    Solo archivos esenciales y rotación mínima
    """
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "[{asctime}] {levelname} {name}: {message}",
                "style": "{",
                "datefmt": "%H:%M:%S"
            },
            "simple": {
                "format": "{levelname} {message}",
                "style": "{",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "level": "INFO",
            },
            "security_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": str(log_dir / "security.log"),
                "formatter": "verbose",
                "maxBytes": 1024 * 1024,  # 1MB
                "backupCount": 3,
                "encoding": "utf-8",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler", 
                "filename": str(log_dir / "errors.log"),
                "formatter": "verbose",
                "level": "ERROR",
                "maxBytes": 1024 * 1024,  # 1MB
                "backupCount": 5,
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": "INFO",
            },
            "usuarios.decorators": {
                "handlers": ["security_file", "console"],
                "level": "INFO",
                "propagate": False,
            },
            "plataforma_cursos.middleware.production_security": {
                "handlers": ["security_file", "console"],
                "level": "INFO",
                "propagate": False,
            },
            "django": {
                "handlers": ["console", "error_file"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }
