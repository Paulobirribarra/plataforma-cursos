"""
Middleware de seguridad específico para Hostinger VPS
Aprovecha el acceso completo al servidor para máxima protección
"""
import os
import time
import logging
import subprocess
from django.http import HttpResponseForbidden, HttpResponse
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout
from django.shortcuts import redirect
import re
import json
from datetime import datetime, timedelta

logger = logging.getLogger('hostinger.security')

class HostingerVPSSecurityMiddleware(MiddlewareMixin):
    """
    Middleware de seguridad que aprovecha las capacidades completas del VPS de Hostinger
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Cargar configuración de seguridad
        self.security_config = getattr(settings, 'HOSTINGER_SECURITY_HEADERS', {})
        self.rate_limits = getattr(settings, 'HOSTINGER_RATE_LIMITS', {})
        
        # Patrones de ataque específicos para VPS
        self.attack_patterns = {
            'sql_injection': [
                r'union.*select', r'drop.*table', r'insert.*into',
                r'delete.*from', r'update.*set', r'exec.*xp_',
                r'sp_executesql', r'@@version', r'information_schema'
            ],
            'xss': [
                r'<script', r'javascript:', r'onload=', r'onerror=',
                r'onclick=', r'onmouseover=', r'eval\(', r'expression\('
            ],
            'path_traversal': [
                r'\.\./', r'\.\.\\', r'/etc/passwd', r'/proc/version',
                r'boot\.ini', r'win\.ini', r'config\.inc'
            ],
            'command_injection': [
                r';\s*(ls|cat|pwd|id|whoami)', r'\|\s*(nc|netcat|wget|curl)',
                r'`[^`]*`', r'\$\([^)]*\)', r'exec\s*\('
            ],
            'scanner_probes': [
                r'wp-admin', r'phpmyadmin', r'admin\.php', r'login\.php',
                r'\.git/', r'\.svn/', r'\.env', r'config\.php'
            ]
        }
        
        super().__init__(get_response)
    
    def process_request(self, request):
        """Análisis completo de seguridad antes de procesar request"""
        
        client_ip = self._get_client_ip(request)
        
        # 1. Verificar si la IP está en lista negra
        if self._is_ip_blocked(client_ip):
            logger.critical(f"🚨 IP bloqueada intentando acceder: {client_ip}")
            return HttpResponseForbidden("Su IP ha sido bloqueada por actividad sospechosa")
        
        # 2. Análisis de patrones de ataque
        threat_level = self._analyze_request_threats(request)
        if threat_level >= 3:  # Nivel crítico
            self._block_ip(client_ip, duration=3600)  # Bloquear 1 hora
            logger.critical(f"🚨 ATAQUE DETECTADO: {client_ip} - Nivel {threat_level}")
            return HttpResponseForbidden("Actividad maliciosa detectada")
        
        # 3. Rate limiting avanzado
        if self._check_advanced_rate_limit(request):
            logger.warning(f"⚠️ Rate limit excedido: {client_ip}")
            return HttpResponseForbidden("Demasiadas solicitudes")
        
        # 4. Verificaciones específicas de admin
        if self._is_admin_request(request):
            admin_check = self._verify_admin_access(request)
            if admin_check:
                return admin_check
        
        # 5. Análisis de User-Agent
        if self._is_suspicious_user_agent(request):
            logger.warning(f"⚠️ User-Agent sospechoso: {client_ip} - {request.META.get('HTTP_USER_AGENT', '')}")
            self._increment_threat_score(client_ip)
        
        return None
    
    def process_response(self, request, response):
        """Aplicar headers de seguridad y logging"""
        
        # Aplicar todos los headers de seguridad
        for header, value in self.security_config.items():
            response[header] = value
        
        # Header adicional con información del servidor
        response['X-Powered-By'] = 'Hostinger-VPS-Security'
        
        # Log de respuestas sospechosas
        if response.status_code in [403, 404, 500]:
            client_ip = self._get_client_ip(request)
            logger.info(f"📊 Respuesta {response.status_code}: {client_ip} - {request.path}")
        
        return response
    
    def _get_client_ip(self, request):
        """Obtener IP real considerando proxies de Hostinger"""
        # Hostinger usa CloudFlare en algunos casos
        cf_connecting_ip = request.META.get('HTTP_CF_CONNECTING_IP')
        if cf_connecting_ip:
            return cf_connecting_ip
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        
        x_real_ip = request.META.get('HTTP_X_REAL_IP')
        if x_real_ip:
            return x_real_ip
        
        return request.META.get('REMOTE_ADDR', '0.0.0.0')
    
    def _analyze_request_threats(self, request):
        """Análisis completo de amenazas en la request"""
        threat_level = 0
        full_path = request.get_full_path().lower()
        query_string = request.META.get('QUERY_STRING', '').lower()
        post_data = str(request.POST).lower() if hasattr(request, 'POST') else ''
        
        # Analizar cada categoría de ataque
        for attack_type, patterns in self.attack_patterns.items():
            for pattern in patterns:
                if (re.search(pattern, full_path, re.IGNORECASE) or
                    re.search(pattern, query_string, re.IGNORECASE) or
                    re.search(pattern, post_data, re.IGNORECASE)):
                    
                    threat_level += 1
                    logger.warning(f"🔍 Patrón {attack_type} detectado: {pattern}")
        
        return threat_level
    
    def _check_advanced_rate_limit(self, request):
        """Rate limiting avanzado con escalamiento de penalizaciones"""
        client_ip = self._get_client_ip(request)
        
        # Determinar tipo de request y límites
        if self._is_login_request(request):
            limit_type = 'login'
        elif self._is_admin_request(request):
            limit_type = 'admin'
        elif self._is_api_request(request):
            limit_type = 'api'
        else:
            limit_type = 'general'
        
        if limit_type not in self.rate_limits:
            return False
        
        limit_config = self.rate_limits[limit_type]
        cache_key = f"hostinger_rate_{limit_type}_{client_ip}"
        
        # Obtener contador actual
        current_data = cache.get(cache_key, {'count': 0, 'violations': 0})
        
        # Verificar límite
        if current_data['count'] >= limit_config['requests']:
            # Escalar penalización por violaciones repetidas
            violation_multiplier = min(current_data['violations'] + 1, 5)
            block_duration = limit_config.get('block_duration', 300) * violation_multiplier
            
            # Bloquear IP temporalmente
            self._block_ip(client_ip, duration=block_duration)
            
            # Incrementar contador de violaciones
            current_data['violations'] += 1
            cache.set(cache_key, current_data, limit_config['window'] * 2)
            
            return True
        
        # Incrementar contador
        current_data['count'] += 1
        cache.set(cache_key, current_data, limit_config['window'])
        
        return False
    
    def _block_ip(self, ip, duration=3600):
        """Bloquear IP usando iptables (disponible en VPS)"""
        try:
            # Agregar IP a lista negra en cache
            cache_key = f"blocked_ip_{ip}"
            cache.set(cache_key, {
                'blocked_at': time.time(),
                'duration': duration,
                'reason': 'Security violation'
            }, duration)
            
            # En VPS real, usar iptables para bloqueo a nivel de red
            if hasattr(settings, 'USE_IPTABLES_BLOCKING') and settings.USE_IPTABLES_BLOCKING:
                subprocess.run([
                    'sudo', 'iptables', '-A', 'INPUT', 
                    '-s', ip, '-j', 'DROP'
                ], capture_output=True)
                
                # Programar desbloqueo automático
                subprocess.run([
                    'echo', f'sudo iptables -D INPUT -s {ip} -j DROP',
                    '|', 'at', f'now + {duration//60} minutes'
                ], shell=True, capture_output=True)
            
            logger.critical(f"🔒 IP bloqueada: {ip} por {duration} segundos")
            
        except Exception as e:
            logger.error(f"Error bloqueando IP {ip}: {e}")
    
    def _is_ip_blocked(self, ip):
        """Verificar si una IP está bloqueada"""
        cache_key = f"blocked_ip_{ip}"
        block_data = cache.get(cache_key)
        
        if block_data:
            if time.time() - block_data['blocked_at'] < block_data['duration']:
                return True
            else:
                # Bloqueo expirado, remover de cache
                cache.delete(cache_key)
        
        return False
    
    def _increment_threat_score(self, ip):
        """Incrementar puntuación de amenaza para una IP"""
        cache_key = f"threat_score_{ip}"
        current_score = cache.get(cache_key, 0)
        new_score = current_score + 1
        
        # Si la puntuación es muy alta, bloquear preventivamente
        if new_score >= 10:
            self._block_ip(ip, duration=1800)  # 30 minutos
            logger.warning(f"⚠️ IP bloqueada preventivamente por alta puntuación: {ip}")
        else:
            cache.set(cache_key, new_score, 3600)  # 1 hora
    
    def _is_suspicious_user_agent(self, request):
        """Detectar User-Agents sospechosos"""
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        
        suspicious_agents = [
            'curl', 'wget', 'python-requests', 'python-urllib',
            'scanner', 'bot', 'crawler', 'spider', 'scraper',
            'nikto', 'sqlmap', 'nmap', 'masscan'
        ]
        
        # Excepciones para bots legítimos
        legitimate_bots = [
            'googlebot', 'bingbot', 'slurp', 'duckduckbot',
            'facebookexternalhit', 'twitterbot'
        ]
        
        for legit in legitimate_bots:
            if legit in user_agent:
                return False
        
        for suspicious in suspicious_agents:
            if suspicious in user_agent:
                return True
        
        # User-Agent muy corto o vacío
        if len(user_agent) < 10:
            return True
        
        return False
    
    def _is_login_request(self, request):
        """Detectar requests de login"""
        return (
            'login' in request.path.lower() or
            'auth' in request.path.lower() or
            (request.method == 'POST' and 'password' in str(request.POST))
        )
    
    def _is_admin_request(self, request):
        """Detectar requests administrativas"""
        admin_secret = getattr(settings, 'ADMIN_URL_SECRET', 'admin')
        return (
            request.path.startswith(f'/{admin_secret}/') or
            'admin' in request.path.lower()
        )
    
    def _is_api_request(self, request):
        """Detectar requests de API"""
        return (
            request.path.startswith('/api/') or
            'application/json' in request.META.get('CONTENT_TYPE', '') or
            'application/json' in request.META.get('HTTP_ACCEPT', '')
        )
    
    def _verify_admin_access(self, request):
        """Verificaciones adicionales para acceso administrativo"""
        
        # Verificar IP whitelist para admin
        admin_whitelist = getattr(settings, 'ADMIN_IP_WHITELIST', [])
        if admin_whitelist:
            client_ip = self._get_client_ip(request)
            if client_ip not in admin_whitelist:
                logger.critical(f"🚨 Acceso admin desde IP no autorizada: {client_ip}")
                return HttpResponseForbidden("Acceso administrativo no autorizado desde esta IP")
        
        # Verificar horario de acceso administrativo
        admin_hours = getattr(settings, 'ADMIN_ALLOWED_HOURS', None)
        if admin_hours:
            current_hour = datetime.now().hour
            if current_hour not in range(admin_hours['start'], admin_hours['end']):
                logger.warning(f"⚠️ Intento de acceso admin fuera de horario: {current_hour}h")
                return HttpResponseForbidden("Acceso administrativo solo permitido en horario laboral")
        
        return None


class HostingerRateLimitMiddleware(MiddlewareMixin):
    """
    Rate limiting específico y más agresivo para VPS
    """
    
    def process_request(self, request):
        """Rate limiting por endpoint específico"""
        
        # Rate limiting por endpoint específico
        endpoint_limits = {
            '/contact/': {'requests': 5, 'window': 300},
            '/newsletter/subscribe/': {'requests': 3, 'window': 600},
            '/payments/': {'requests': 10, 'window': 300},
        }
        
        for endpoint, limit_config in endpoint_limits.items():
            if request.path.startswith(endpoint):
                client_ip = self._get_client_ip(request)
                cache_key = f"endpoint_limit_{endpoint}_{client_ip}"
                
                current_count = cache.get(cache_key, 0)
                if current_count >= limit_config['requests']:
                    logger.warning(f"⚠️ Rate limit en {endpoint}: {client_ip}")
                    return HttpResponseForbidden(f"Demasiadas solicitudes a {endpoint}")
                
                cache.set(cache_key, current_count + 1, limit_config['window'])
        
        return None
    
    def _get_client_ip(self, request):
        """Obtener IP del cliente"""
        cf_connecting_ip = request.META.get('HTTP_CF_CONNECTING_IP')
        if cf_connecting_ip:
            return cf_connecting_ip
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        
        return request.META.get('REMOTE_ADDR', '0.0.0.0')


class HostingerFirewallMiddleware(MiddlewareMixin):
    """
    Firewall a nivel de aplicación para VPS
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Países bloqueados (códigos ISO)
        self.blocked_countries = getattr(settings, 'BLOCKED_COUNTRIES', [])
        
        # IPs permitidas específicas
        self.allowed_ips = getattr(settings, 'ALLOWED_IPS', [])
        
        super().__init__(get_response)
    
    def process_request(self, request):
        """Firewall a nivel de aplicación"""
        
        client_ip = self._get_client_ip(request)
        
        # Verificar lista blanca
        if self.allowed_ips and client_ip not in self.allowed_ips:
            # Solo para endpoints críticos
            critical_endpoints = ['/admin/', '/payments/', '/api/']
            if any(request.path.startswith(endpoint) for endpoint in critical_endpoints):
                logger.warning(f"⚠️ Acceso denegado a endpoint crítico desde IP no autorizada: {client_ip}")
                return HttpResponseForbidden("Acceso no autorizado")
        
        return None
    
    def _get_client_ip(self, request):
        """Obtener IP del cliente"""
        cf_connecting_ip = request.META.get('HTTP_CF_CONNECTING_IP')
        if cf_connecting_ip:
            return cf_connecting_ip
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        
        return request.META.get('REMOTE_ADDR', '0.0.0.0')
