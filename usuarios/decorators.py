"""
Sistema de decoradores de seguridad para roles específicos
Proporciona protección granular para diferentes niveles de acceso
"""
from functools import wraps
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# FUNCIONES DE VERIFICACIÓN DE ROLES
# =============================================================================

def is_superuser(user):
    """Verifica si el usuario es superuser"""
    return user.is_authenticated and user.is_superuser

def is_staff_user(user):
    """Verifica si el usuario es staff"""
    return user.is_authenticated and user.is_staff

def is_admin_user(user):
    """Verifica si el usuario es admin (staff o superuser)"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def is_active_user(user):
    """Verifica si el usuario está activo"""
    return user.is_authenticated and user.is_active

def can_manage_content(user):
    """Verifica si el usuario puede gestionar contenido (blogs, boletines, cursos)"""
    return is_admin_user(user) and user.is_active

def can_manage_users(user):
    """Verifica si el usuario puede gestionar otros usuarios"""
    return user.is_authenticated and user.is_superuser and user.is_active

def can_access_admin_panel(user):
    """Verifica acceso completo al panel de administración"""
    return user.is_authenticated and user.is_staff and user.is_active

# =============================================================================
# DECORADORES DE SEGURIDAD
# =============================================================================

def superuser_required(view_func=None, *, redirect_url='/usuarios/dashboard/', message=None):
    """
    Decorador que requiere que el usuario sea superuser
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.info(request, 'Debes iniciar sesión para continuar.')
                return redirect('account_login')
            
            if not is_superuser(request.user):
                default_message = 'Necesitas permisos de superusuario para acceder a esta función.'
                messages.error(request, message or default_message)
                logger.warning(
                    f"Usuario {request.user.username} sin permisos de superuser "
                    f"intentó acceder a {request.path} desde IP: {request.META.get('REMOTE_ADDR', 'Unknown')}"
                )
                return redirect(redirect_url)
            
            return func(request, *args, **kwargs)
        return wrapper
    
    if view_func is None:
        return decorator
    else:
        return decorator(view_func)

def content_manager_required(view_func=None, *, redirect_url='/usuarios/dashboard/', message=None):
    """
    Decorador para gestores de contenido (blogs, boletines, cursos)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.info(request, 'Debes iniciar sesión para continuar.')
                return redirect('account_login')
            
            if not can_manage_content(request.user):
                default_message = 'No tienes permisos para gestionar contenido.'
                messages.error(request, message or default_message)
                logger.warning(
                    f"Usuario {request.user.username} sin permisos de gestión de contenido "
                    f"intentó acceder a {request.path} desde IP: {request.META.get('REMOTE_ADDR', 'Unknown')}"
                )
                return redirect(redirect_url)
            
            return func(request, *args, **kwargs)
        return wrapper
    
    if view_func is None:
        return decorator
    else:
        return decorator(view_func)

def admin_panel_required(view_func=None, *, redirect_url='/usuarios/dashboard/', message=None):
    """
    Decorador específico para acceso al panel de administración
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.info(request, 'Debes iniciar sesión para continuar.')
                return redirect('account_login')
            
            if not can_access_admin_panel(request.user):
                default_message = 'No tienes permisos para acceder al panel de administración.'
                messages.error(request, message or default_message)
                logger.warning(
                    f"Usuario {request.user.username} sin permisos de admin "
                    f"intentó acceder a {request.path} desde IP: {request.META.get('REMOTE_ADDR', 'Unknown')}"
                )
                return redirect(redirect_url)
            
            # Verificar que la cuenta esté activa
            if not request.user.is_active:
                messages.error(request, 'Tu cuenta está desactivada. Contacta al administrador.')
                logger.warning(
                    f"Usuario inactivo {request.user.username} intentó acceder al admin "
                    f"desde IP: {request.META.get('REMOTE_ADDR', 'Unknown')}"
                )
                return redirect('/')
            
            # Log de acceso exitoso para auditoría
            logger.info(
                f"Acceso de admin autorizado: usuario {request.user.username} "
                f"({request.method} {request.path}) desde IP: {request.META.get('REMOTE_ADDR', 'Unknown')}"
            )
            
            return func(request, *args, **kwargs)
        return wrapper
    
    if view_func is None:
        return decorator
    else:
        return decorator(view_func)

def user_manager_required(view_func=None, *, redirect_url='/usuarios/dashboard/', message=None):
    """
    Decorador para gestión de usuarios (solo superusers)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.info(request, 'Debes iniciar sesión para continuar.')
                return redirect('account_login')
            
            if not can_manage_users(request.user):
                default_message = 'Solo los superusuarios pueden gestionar usuarios.'
                messages.error(request, message or default_message)
                logger.warning(
                    f"Usuario {request.user.username} sin permisos de gestión de usuarios "
                    f"intentó acceder a {request.path} desde IP: {request.META.get('REMOTE_ADDR', 'Unknown')}"
                )
                return redirect(redirect_url)
            
            return func(request, *args, **kwargs)
        return wrapper
    
    if view_func is None:
        return decorator
    else:
        return decorator(view_func)

# =============================================================================
# MIXINS PARA VISTAS BASADAS EN CLASES
# =============================================================================

class SuperuserRequiredMixin:
    """Mixin que requiere permisos de superuser"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, 'Debes iniciar sesión para continuar.')
            return redirect('account_login')
        
        if not is_superuser(request.user):
            messages.error(request, 'Necesitas permisos de superusuario para acceder a esta función.')
            logger.warning(
                f"Usuario {request.user.username} sin permisos de superuser "
                f"intentó acceder a {request.path} desde IP: {request.META.get('REMOTE_ADDR', 'Unknown')}"
            )
            return redirect('/usuarios/dashboard/')
        
        return super().dispatch(request, *args, **kwargs)

class ContentManagerRequiredMixin:
    """Mixin para gestores de contenido"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, 'Debes iniciar sesión para continuar.')
            return redirect('account_login')
        
        if not can_manage_content(request.user):
            messages.error(request, 'No tienes permisos para gestionar contenido.')
            logger.warning(
                f"Usuario {request.user.username} sin permisos de gestión de contenido "
                f"intentó acceder a {request.path} desde IP: {request.META.get('REMOTE_ADDR', 'Unknown')}"
            )
            return redirect('/usuarios/dashboard/')
        
        return super().dispatch(request, *args, **kwargs)

class AdminPanelRequiredMixin:
    """Mixin para acceso al panel de administración"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, 'Debes iniciar sesión para continuar.')
            return redirect('account_login')
        
        if not can_access_admin_panel(request.user):
            messages.error(request, 'No tienes permisos para acceder al panel de administración.')
            logger.warning(
                f"Usuario {request.user.username} sin permisos de admin "
                f"intentó acceder a {request.path} desde IP: {request.META.get('REMOTE_ADDR', 'Unknown')}"
            )
            return redirect('/usuarios/dashboard/')
        
        if not request.user.is_active:
            messages.error(request, 'Tu cuenta está desactivada. Contacta al administrador.')
            logger.warning(
                f"Usuario inactivo {request.user.username} intentó acceder al admin "
                f"desde IP: {request.META.get('REMOTE_ADDR', 'Unknown')}"
            )
            return redirect('/')
        
        # Log de acceso exitoso
        logger.info(
            f"Acceso de admin autorizado: usuario {request.user.username} "
            f"({request.method} {request.path}) desde IP: {request.META.get('REMOTE_ADDR', 'Unknown')}"
        )
        
        return super().dispatch(request, *args, **kwargs)

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def get_client_ip(request):
    """Obtiene la IP real del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_security_event(user, event_type, details, request=None):
    """Log eventos de seguridad con detalles completos"""
    ip = get_client_ip(request) if request else 'Unknown'
    user_info = user.username if user.is_authenticated else 'Anonymous'
    
    logger.warning(
        f"SECURITY_EVENT: {event_type} | User: {user_info} | IP: {ip} | Details: {details}"
    )
