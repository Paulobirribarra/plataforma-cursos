"""
Middleware de seguridad de producción para protección integral
Incluye rate limiting, headers de seguridad y monitoreo avanzado
"""
import time
import hashlib
import logging
from collections import defaultdict, deque
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout
from django.urls import reverse
from usuarios.decorators import get_client_ip, log_security_event
from plataforma_cursos.security_alerts import (
    send_failed_login_alert, 
    send_suspicious_activity_alert,
    send_critical_security_alert
)

logger = logging.getLogger(__name__)

class ProductionSecurityMiddleware(MiddlewareMixin):
    """
    Middleware de seguridad para entorno de producción
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Rate limiting - Configuración
        self.rate_limits = {
            'login': {'requests': 5, 'window': 300},  # 5 intentos por 5 minutos
            'admin': {'requests': 20, 'window': 300},  # 20 requests por 5 minutos para admin
            'api': {'requests': 100, 'window': 300},   # 100 requests por 5 minutos para API
            'general': {'requests': 200, 'window': 300}  # 200 requests por 5 minutos general
        }
        
        # Rutas que requieren rate limiting especial
        self.protected_paths = {
            '/account/login/': 'login',
            '/account/signup/': 'login',
            '/secret-admin-panel/': 'admin',
            '/api/': 'api',
        }
        
        # IPs bloqueadas temporalmente
        self.blocked_ips = set()
        
        super().__init__(get_response)
    
    def __call__(self, request):
        # Verificar rate limiting antes de procesar
        if not self._check_rate_limit(request):
            return self._rate_limit_response(request)
        
        # Verificar IP bloqueada
        if self._is_ip_blocked(request):
            return self._blocked_ip_response(request)
        
        # Procesar request
        response = self.get_response(request)
        
        # Agregar headers de seguridad
        response = self._add_security_headers(response, request)
        
        return response
    
    def _check_rate_limit(self, request):
        """Verificar límites de rate limiting"""
        if not getattr(settings, 'ENABLE_RATE_LIMITING', True):
            return True
        
        client_ip = get_client_ip(request)
        
        # Determinar el tipo de límite a aplicar
        limit_type = 'general'
        for path, path_type in self.protected_paths.items():
            if request.path.startswith(path):
                limit_type = path_type
                break
        
        # Crear clave única para el rate limiting
        cache_key = f"rate_limit:{limit_type}:{client_ip}"
        
        # Obtener configuración del límite
        limit_config = self.rate_limits.get(limit_type, self.rate_limits['general'])
        max_requests = limit_config['requests']
        window_seconds = limit_config['window']
        
        # Verificar en cache
        current_requests = cache.get(cache_key, 0)
        if current_requests >= max_requests:
            # Log del rate limit excedido
            log_security_event(
                request.user,
                'RATE_LIMIT_EXCEEDED',
                f"Type: {limit_type}, Requests: {current_requests}, Max: {max_requests}",
                request
            )
            
            # Enviar alerta de seguridad para rate limiting crítico
            if limit_type in ['login', 'admin']:
                try:
                    send_suspicious_activity_alert(
                        ip_address=client_ip,
                        activity_details={
                            'type': 'rate_limit_violation',
                            'description': f'Rate limit excedido para {limit_type}: {current_requests}/{max_requests}',
                            'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
                            'path': request.path,
                            'limit_type': limit_type
                        }
                    )
                except Exception as e:
                    logger.error(f"Error enviando alerta de rate limiting: {e}")
            
            # Bloquear IP si excede límites críticos repetidamente
            if limit_type in ['login', 'admin'] and current_requests > max_requests * 2:
                self._block_ip_temporarily(client_ip, 3600)  # Bloquear por 1 hora
                
                # Alerta crítica por bloqueo de IP
                try:
                    send_critical_security_alert(
                        threat_type='ip_blocked',
                        details={
                            'ip_address': client_ip,
                            'reason': f'Rate limit excedido crítico: {current_requests}/{max_requests}',
                            'path': request.path,
                            'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
                            'block_duration': '1 hora'
                        }
                    )
                except Exception as e:
                    logger.error(f"Error enviando alerta crítica: {e}")
            
            return False
        
        # Incrementar contador
        cache.set(cache_key, current_requests + 1, window_seconds)
        return True
    
    def _rate_limit_response(self, request):
        """Respuesta cuando se excede el rate limit"""
        if request.path.startswith('/api/'):
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please try again later.',
                'retry_after': 300
            }, status=429)
        
        messages.error(request, 'Demasiadas solicitudes. Intenta de nuevo en unos minutos.')
        return redirect('/')
    
    def _is_ip_blocked(self, request):
        """Verificar si la IP está bloqueada"""
        client_ip = get_client_ip(request)
        blocked_key = f"blocked_ip:{client_ip}"
        return cache.get(blocked_key, False)
    
    def _block_ip_temporarily(self, ip, duration_seconds):
        """Bloquear IP temporalmente"""
        blocked_key = f"blocked_ip:{ip}"
        cache.set(blocked_key, True, duration_seconds)
        
        logger.critical(f"IP {ip} blocked temporarily for {duration_seconds} seconds due to suspicious activity")
    
    def _blocked_ip_response(self, request):
        """Respuesta para IPs bloqueadas"""
        log_security_event(
            request.user,
            'BLOCKED_IP_ACCESS_ATTEMPT',
            f"Blocked IP tried to access {request.path}",
            request
        )
        
        return HttpResponse(
            "<h1>Access Denied</h1><p>Your IP has been temporarily blocked due to suspicious activity.</p>",
            status=403
        )
    
    def _add_security_headers(self, response, request):
        """Agregar headers de seguridad"""
        
        # Headers básicos de seguridad
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        }
        
        # HTTPS headers (solo en producción)
        if not settings.DEBUG:
            security_headers.update({
                'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
                'Content-Security-Policy': self._get_csp_header(),
            })
        
        # Aplicar headers
        for header, value in security_headers.items():
            response[header] = value
        
        # Headers específicos para admin
        if request.path.startswith('/secret-admin-panel/'):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response
    
    def _get_csp_header(self):
        """Generar Content Security Policy header"""
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com",
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com",
            "img-src 'self' data: https:",
            "font-src 'self' https://cdnjs.cloudflare.com",
            "connect-src 'self'",
            "frame-src 'none'",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]
        
        return "; ".join(csp_directives)

class AdminAccessAuditMiddleware(MiddlewareMixin):
    """
    Middleware específico para auditar accesos al panel de administración
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.admin_paths = ['/secret-admin-panel/', '/admin/']
        super().__init__(get_response)
    
    def __call__(self, request):
        # Verificar si es acceso a admin
        is_admin_access = any(request.path.startswith(path) for path in self.admin_paths)
        
        if is_admin_access:
            self._audit_admin_access(request)
        
        response = self.get_response(request)
        
        if is_admin_access:
            self._audit_admin_response(request, response)
        
        return response
    
    def _audit_admin_access(self, request):
        """Auditar acceso al panel de administración"""
        client_ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        
        audit_data = {
            'timestamp': time.time(),
            'user': request.user.username if request.user.is_authenticated else 'Anonymous',
            'ip': client_ip,
            'path': request.path,
            'method': request.method,
            'user_agent': user_agent,
            'session_key': request.session.session_key,
        }
        
        # Log detallado para admin
        logger.info(f"ADMIN_ACCESS: {audit_data}")
        
        # Verificar patrones sospechosos
        self._check_suspicious_patterns(request, audit_data)
    
    def _audit_admin_response(self, request, response):
        """Auditar respuesta del panel de administración"""
        if response.status_code >= 400:
            log_security_event(
                request.user,
                'ADMIN_ACCESS_ERROR',
                f"Status: {response.status_code}, Path: {request.path}",
                request
            )
    
    def _check_suspicious_patterns(self, request, audit_data):
        """Verificar patrones sospechosos en accesos admin"""
        client_ip = audit_data['ip']
        
        # Verificar múltiples intentos de acceso rápidos
        recent_attempts_key = f"admin_attempts:{client_ip}"
        recent_attempts = cache.get(recent_attempts_key, [])
        
        current_time = time.time()
        # Mantener solo intentos de los últimos 5 minutos
        recent_attempts = [t for t in recent_attempts if current_time - t < 300]
        recent_attempts.append(current_time)
        
        cache.set(recent_attempts_key, recent_attempts, 300)
        
        # Si hay más de 10 intentos en 5 minutos, es sospechoso
        if len(recent_attempts) > 10:
            log_security_event(
                request.user,
                'SUSPICIOUS_ADMIN_ACTIVITY',
                f"Multiple rapid admin access attempts: {len(recent_attempts)} in 5 minutes",
                request
            )
            
            # Notificar a administradores (implementar según necesidades)
            self._notify_administrators(audit_data, 'SUSPICIOUS_ACTIVITY')
    
    def _notify_administrators(self, audit_data, alert_type):
        """Notificar a administradores sobre actividad sospechosa"""
        # Aquí puedes implementar notificaciones por email, Slack, etc.
        logger.critical(f"SECURITY_ALERT: {alert_type} - {audit_data}")

class SessionSecurityMiddleware(MiddlewareMixin):
    """
    Middleware para mejorar la seguridad de sesiones
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        if request.user.is_authenticated:
            self._check_session_security(request)
        
        response = self.get_response(request)
        return response
    
    def _check_session_security(self, request):
        """Verificar seguridad de la sesión"""
        current_ip = get_client_ip(request)
        session_ip = request.session.get('login_ip')
        
        # Verificar si la IP cambió (posible secuestro de sesión)
        if session_ip and session_ip != current_ip:
            # Para usuarios admin, ser más estrictos
            if request.user.is_staff:
                log_security_event(
                    request.user,
                    'SESSION_IP_CHANGE_ADMIN',
                    f"Session IP changed from {session_ip} to {current_ip}",
                    request
                )
                messages.warning(request, 'Se detectó un cambio de IP. Por seguridad, debes iniciar sesión nuevamente.')
                logout(request)
                return redirect('account_login')
            else:
                # Para usuarios normales, solo log
                log_security_event(
                    request.user,
                    'SESSION_IP_CHANGE_USER',
                    f"Session IP changed from {session_ip} to {current_ip}",
                    request
                )
        
        # Actualizar IP de la sesión
        request.session['login_ip'] = current_ip
        
        # Verificar tiempo de inactividad para admins
        if request.user.is_staff:
            self._check_admin_session_timeout(request)
    
    def _check_admin_session_timeout(self, request):
        """Verificar timeout de sesión para administradores"""
        last_activity = request.session.get('last_activity')
        current_time = time.time()
        
        if last_activity:
            # Timeout de 30 minutos para admins
            admin_timeout = 30 * 60
            if current_time - last_activity > admin_timeout:
                log_security_event(
                    request.user,
                    'ADMIN_SESSION_TIMEOUT',
                    f"Admin session timed out after {admin_timeout} seconds",
                    request
                )
                messages.info(request, 'Tu sesión de administrador ha expirado por inactividad.')
                logout(request)
                return redirect('account_login')
        
        # Actualizar última actividad
        request.session['last_activity'] = current_time
