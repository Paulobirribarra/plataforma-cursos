# plataforma_cursos/middleware/admin_security.py
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseForbidden, Http404
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)

class AdminSecurityMiddleware(MiddlewareMixin):
    """
    Middleware de seguridad para el panel de administración.
    Restringe el acceso al admin solo a usuarios autenticados con permisos de staff.
    Redirecciona amigablemente a usuarios no autorizados.
    """
    
    # URL secreta del admin (debe coincidir con urls.py)
    ADMIN_URL_PATH = '/sistema-gestion-admin-2025/'
    
    def process_request(self, request):
        """
        Procesa cada request antes de que llegue a la vista.
        Verifica acceso al admin y aplica restricciones de seguridad.
        """
        # Verificar si la request es para el admin
        if request.path.startswith(self.ADMIN_URL_PATH):
            return self._check_admin_access(request)
        
        # Bloquear acceso a la URL tradicional /admin/ y redirigir amigablemente
        if request.path.startswith('/admin/'):
            logger.warning(f"Intento de acceso a URL admin tradicional desde IP: {self._get_client_ip(request)}")
            
            if request.user.is_authenticated:
                if request.user.is_staff:
                    # Si es staff, redirigir a la URL secreta
                    return redirect(self.ADMIN_URL_PATH)
                else:
                    # Si no es staff, redirigir al dashboard
                    messages.info(request, 'Acceso no autorizado a esa sección.')
                    return redirect('/usuarios/dashboard/')
            else:
                # Si no está autenticado, redirigir al home
                messages.info(request, 'Por favor, inicia sesión para continuar.')
                return redirect('/')
        
        return None
    
    def _check_admin_access(self, request):
        """
        Verifica el acceso al panel de administración.
        Redirrige a usuarios no autorizados a páginas amigables.
        """
        # Para usuarios no autenticados: redirigir al home
        if not request.user.is_authenticated:
            logger.warning(f"Intento de acceso no autenticado al admin desde IP: {self._get_client_ip(request)}")
            messages.info(request, 'Por favor, inicia sesión para continuar.')
            return redirect('/')
        
        # Para usuarios autenticados pero sin permisos de staff: redirigir al dashboard
        if not request.user.is_staff:
            logger.warning(
                f"Usuario {request.user.username} sin permisos de staff intentó acceder al admin "
                f"desde IP: {self._get_client_ip(request)}"
            )
            messages.warning(request, 'No tienes permisos para acceder a esa sección.')
            # Redirigir al dashboard del usuario
            return redirect('/usuarios/dashboard/')
        
        # Verificar si el usuario está activo
        if not request.user.is_active:
            logger.warning(
                f"Usuario inactivo {request.user.username} intentó acceder al admin "
                f"desde IP: {self._get_client_ip(request)}"
            )
            messages.error(request, 'Tu cuenta está desactivada. Contacta al administrador.')
            logout(request)
            return redirect('/')
        
        # Log de acceso exitoso para auditoría
        if request.method == 'POST' or 'add' in request.path or 'change' in request.path or 'delete' in request.path:
            logger.info(
                f"Acceso de admin autorizado: usuario {request.user.username} "
                f"({request.method} {request.path}) desde IP: {self._get_client_ip(request)}"
            )
        
        return None
    
    def _get_client_ip(self, request):
        """
        Obtiene la IP real del cliente, considerando proxies.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class AdminSessionSecurityMiddleware(MiddlewareMixin):
    """
    Middleware adicional de seguridad para sesiones de admin.
    Implementa timeout automático y validaciones adicionales.
    """
    
    # Timeout de sesión para admin (en segundos) - 2 horas
    ADMIN_SESSION_TIMEOUT = 7200
    # URL secreta del admin (debe coincidir con AdminSecurityMiddleware)
    ADMIN_URL_PATH = '/sistema-gestion-admin-2025/'
    
    def process_request(self, request):
        """
        Verifica la seguridad de la sesión para usuarios admin.
        """
        if not request.path.startswith(self.ADMIN_URL_PATH):
            return None
            
        if not request.user.is_authenticated or not request.user.is_staff:
            return None
        
        # Verificar timeout de sesión
        return self._check_session_timeout(request)
    
    def _check_session_timeout(self, request):
        """
        Verifica si la sesión ha expirado por inactividad.
        """
        import time
        from django.contrib.auth import logout
        
        current_time = time.time()
        last_activity = request.session.get('admin_last_activity')
        
        if last_activity:
            if current_time - last_activity > self.ADMIN_SESSION_TIMEOUT:
                logger.info(
                    f"Sesión de admin expirada por timeout para usuario {request.user.username} "
                    f"desde IP: {self._get_client_ip(request)}"
                )
                logout(request)
                messages.warning(request, 'Tu sesión ha expirado por inactividad. Por favor, inicia sesión nuevamente.')
                return redirect(self.ADMIN_URL_PATH + 'login/')
        
        # Actualizar última actividad
        request.session['admin_last_activity'] = current_time
        request.session.modified = True
        
        return None
    
    def _get_client_ip(self, request):
        """
        Obtiene la IP real del cliente, considerando proxies.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
