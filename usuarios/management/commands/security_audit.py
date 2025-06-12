"""
Comando de gestión para auditoría y configuración de seguridad
Uso: python manage.py security_audit
"""
import os
import time
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from plataforma_cursos.security_config import validate_security_config
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class Command(BaseCommand):
    help = 'Ejecuta auditoría de seguridad y proporciona recomendaciones'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            choices=['audit', 'check-config', 'create-admin', 'reset-failed-logins', 'block-ip', 'unblock-ip', 'hostinger-check', 'production-ready-check'],
            default='audit',
            help='Acción a ejecutar'
        )
        parser.add_argument(
            '--ip',
            type=str,
            help='IP address para bloquear/desbloquear'
        )
        parser.add_argument(
            '--duration',
            type=int,
            default=3600,
            help='Duración del bloqueo en segundos (por defecto: 1 hora)'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        self.stdout.write(self.style.SUCCESS('🔐 Sistema de Auditoría de Seguridad'))
        self.stdout.write('=' * 50)
        
        if action == 'audit':
            self.run_security_audit()
        elif action == 'check-config':
            self.check_configuration()
        elif action == 'create-admin':
            self.create_secure_admin()
        elif action == 'reset-failed-logins':
            self.reset_failed_logins()
        elif action == 'block-ip':
            self.block_ip(options['ip'], options['duration'])
        elif action == 'unblock-ip':
            self.unblock_ip(options['ip'])
        elif action == 'hostinger-check':
            self.stdout.write(self.style.SUCCESS('🏗️ VERIFICACIÓN ESPECÍFICA PARA HOSTINGER VPS'))
            self._check_hostinger_configuration()
        
        elif action == 'production-ready-check':
            self.stdout.write(self.style.SUCCESS('🚀 VERIFICACIÓN DE PRODUCCIÓN COMPLETA'))
            self._check_production_readiness()

    def run_security_audit(self):
        """Ejecutar auditoría completa de seguridad"""
        self.stdout.write('\n📊 EJECUTANDO AUDITORÍA DE SEGURIDAD...\n')
        
        # 1. Verificar configuración
        self.check_configuration()
        
        # 2. Auditar usuarios
        self.audit_users()
        
        # 3. Verificar sesiones activas
        self.audit_sessions()
        
        # 4. Revisar intentos de acceso
        self.audit_access_attempts()
        
        # 5. Verificar middleware de seguridad
        self.audit_middleware()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Auditoría de seguridad completada'))

    def check_configuration(self):
        """Verificar configuración de seguridad"""
        self.stdout.write('\n🔧 VERIFICANDO CONFIGURACIÓN...')
        
        issues = []
        
        # Verificar DEBUG
        if settings.DEBUG:
            issues.append('❌ DEBUG=True en producción es inseguro')
        else:
            self.stdout.write('✅ DEBUG deshabilitado')
        
        # Verificar SECRET_KEY
        if len(settings.SECRET_KEY) < 50:
            issues.append('❌ SECRET_KEY demasiado corta')
        else:
            self.stdout.write('✅ SECRET_KEY tiene longitud adecuada')
        
        # Verificar ALLOWED_HOSTS
        if '*' in settings.ALLOWED_HOSTS and not settings.DEBUG:
            issues.append('❌ ALLOWED_HOSTS permite todos los hosts en producción')
        else:
            self.stdout.write('✅ ALLOWED_HOSTS configurado correctamente')
        
        # Verificar middleware de seguridad
        security_middlewares = [
            'django.middleware.security.SecurityMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'plataforma_cursos.middleware.admin_security.AdminSecurityMiddleware',
        ]
        
        for middleware in security_middlewares:
            if middleware in settings.MIDDLEWARE:
                self.stdout.write(f'✅ {middleware.split(".")[-1]} activo')
            else:
                issues.append(f'❌ {middleware} no está activo')
        
        # Verificar configuración de sesiones
        if not settings.DEBUG:
            if not getattr(settings, 'SESSION_COOKIE_SECURE', False):
                issues.append('❌ SESSION_COOKIE_SECURE debería estar en True')
            if not getattr(settings, 'CSRF_COOKIE_SECURE', False):
                issues.append('❌ CSRF_COOKIE_SECURE debería estar en True')
        
        # Mostrar problemas encontrados
        if issues:
            self.stdout.write('\n🚨 PROBLEMAS DE CONFIGURACIÓN ENCONTRADOS:')
            for issue in issues:
                self.stdout.write(f'  {issue}')
        else:
            self.stdout.write('✅ Configuración de seguridad correcta')
        
        # Ejecutar validación adicional
        validate_security_config()

    def audit_users(self):
        """Auditar usuarios del sistema"""
        self.stdout.write('\n👥 AUDITANDO USUARIOS...')
        
        # Usuarios con privilegios administrativos
        admin_users = User.objects.filter(is_staff=True)
        superusers = User.objects.filter(is_superuser=True)
        
        self.stdout.write(f'📈 Estadísticas de usuarios:')
        self.stdout.write(f'  Total usuarios: {User.objects.count()}')
        self.stdout.write(f'  Usuarios staff: {admin_users.count()}')
        self.stdout.write(f'  Superusuarios: {superusers.count()}')
        
        # Verificar superusuarios
        if superusers.count() > 3:
            self.stdout.write('⚠️ Demasiados superusuarios (recomendado: máximo 3)')
        
        # Mostrar usuarios administrativos
        self.stdout.write('\n🔑 Usuarios con privilegios administrativos:')
        for user in admin_users:
            status = '🟢' if user.is_active else '🔴'
            su_marker = ' (SUPERUSER)' if user.is_superuser else ''
            last_login = user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Nunca'
            self.stdout.write(f'  {status} {user.email}{su_marker} - Último login: {last_login}')
        
        # Usuarios inactivos con privilegios
        inactive_admins = admin_users.filter(is_active=False)
        if inactive_admins.exists():
            self.stdout.write('\n⚠️ Usuarios administrativos inactivos:')
            for user in inactive_admins:
                self.stdout.write(f'  🔴 {user.email}')

    def audit_sessions(self):
        """Auditar sesiones activas"""
        self.stdout.write('\n🔐 AUDITANDO SESIONES...')
        
        try:
            from django.contrib.sessions.models import Session
            from django.utils import timezone
            
            active_sessions = Session.objects.filter(expire_date__gt=timezone.now())
            self.stdout.write(f'📊 Sesiones activas: {active_sessions.count()}')
            
            # Verificar sesiones de administradores
            admin_sessions = 0
            for session in active_sessions:
                session_data = session.get_decoded()
                user_id = session_data.get('_auth_user_id')
                if user_id:
                    try:
                        user = User.objects.get(id=user_id)
                        if user.is_staff:
                            admin_sessions += 1
                    except User.DoesNotExist:
                        pass
            
            self.stdout.write(f'👤 Sesiones de administradores: {admin_sessions}')
            
        except Exception as e:
            self.stdout.write(f'❌ Error auditando sesiones: {e}')

    def audit_access_attempts(self):
        """Auditar intentos de acceso recientes"""
        self.stdout.write('\n🚪 AUDITANDO INTENTOS DE ACCESO...')
        
        # Verificar intentos de rate limiting recientes
        try:
            # Buscar claves de rate limiting en cache
            cache_keys = []
            if hasattr(cache, '_cache') and hasattr(cache._cache, 'keys'):
                cache_keys = [key for key in cache._cache.keys() if 'rate_limit' in str(key)]
            
            if cache_keys:
                self.stdout.write(f'🔍 Intentos de rate limiting detectados: {len(cache_keys)}')
                
                # Mostrar algunos ejemplos (sin exponer IPs completas)
                for key in cache_keys[:5]:
                    count = cache.get(key, 0)
                    if count > 0:
                        key_parts = str(key).split(':')
                        if len(key_parts) >= 3:
                            rate_type = key_parts[1]
                            ip_masked = key_parts[2][:8] + '***' if len(key_parts[2]) > 8 else '***'
                            self.stdout.write(f'  📍 {rate_type}: {ip_masked} - {count} intentos')
            else:
                self.stdout.write('✅ No se detectaron intentos de rate limiting recientes')
                
        except Exception as e:
            self.stdout.write(f'⚠️ No se pudo verificar cache de rate limiting: {e}')

    def audit_middleware(self):
        """Auditar middleware de seguridad"""
        self.stdout.write('\n🛡️ AUDITANDO MIDDLEWARE...')
        
        security_middleware = [
            ('SecurityMiddleware', 'django.middleware.security.SecurityMiddleware'),
            ('CSRFMiddleware', 'django.middleware.csrf.CsrfViewMiddleware'),
            ('AdminSecurityMiddleware', 'plataforma_cursos.middleware.admin_security.AdminSecurityMiddleware'),
        ]
        
        for name, middleware in security_middleware:
            if middleware in settings.MIDDLEWARE:
                self.stdout.write(f'✅ {name} activo')
            else:
                self.stdout.write(f'❌ {name} NO activo')

    def create_secure_admin(self):
        """Crear un usuario administrador seguro"""
        self.stdout.write('\n👤 CREANDO USUARIO ADMINISTRADOR SEGURO...')
        
        email = input('Email del administrador: ')
        username = input('Username del administrador: ')
        
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR(f'❌ Ya existe un usuario con email {email}'))
            return
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'❌ Ya existe un usuario con username {username}'))
            return
        
        # Crear usuario con configuraciones de seguridad
        user = User.objects.create_user(
            email=email,
            username=username,
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )
        
        # Configurar password segura (será solicitada en primera sesión)
        temp_password = User.objects.make_random_password(length=20)
        user.set_password(temp_password)
        user.save()
        
        self.stdout.write(self.style.SUCCESS(f'✅ Usuario administrador creado: {email}'))
        self.stdout.write(f'🔑 Password temporal: {temp_password}')
        self.stdout.write('⚠️ IMPORTANTE: Cambiar la password en el primer login')

    def reset_failed_logins(self):
        """Resetear intentos de login fallidos"""
        self.stdout.write('\n🔄 RESETEANDO INTENTOS DE LOGIN FALLIDOS...')
        
        # Resetear contadores de failed_login_attempts
        users_with_failed_logins = User.objects.filter(failed_login_attempts__gt=0)
        count = users_with_failed_logins.count()
        
        users_with_failed_logins.update(
            failed_login_attempts=0,
            account_locked_until=None
        )
        
        self.stdout.write(self.style.SUCCESS(f'✅ Reseteados intentos fallidos para {count} usuarios'))

    def block_ip(self, ip, duration):
        """Bloquear una IP específica"""
        if not ip:
            ip = input('IP a bloquear: ')
        
        blocked_key = f"blocked_ip:{ip}"
        cache.set(blocked_key, True, duration)
        
        self.stdout.write(self.style.SUCCESS(f'🚫 IP {ip} bloqueada por {duration} segundos'))
        logger.warning(f"IP {ip} blocked manually via management command for {duration} seconds")

    def unblock_ip(self, ip):
        """Desbloquear una IP específica"""
        if not ip:
            ip = input('IP a desbloquear: ')
        
        blocked_key = f"blocked_ip:{ip}"
        cache.delete(blocked_key)
        
        self.stdout.write(self.style.SUCCESS(f'✅ IP {ip} desbloqueada'))
        logger.info(f"IP {ip} unblocked manually via management command")

    def _check_hostinger_configuration(self):
        """Verificaciones específicas para Hostinger VPS"""
        self.stdout.write('\n📊 VERIFICANDO CONFIGURACIÓN HOSTINGER:')
        
        checks = []
        
        # Verificar configuración de base de datos MySQL
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
                if 'mysql' in version.lower() or 'mariadb' in version.lower():
                    checks.append(('✅', f'Base de datos MySQL/MariaDB: {version}'))
                else:
                    checks.append(('❌', f'Base de datos no es MySQL: {version}'))
        except Exception as e:
            checks.append(('❌', f'Error conectando a base de datos: {e}'))
        
        # Verificar configuración SSL
        ssl_enabled = getattr(settings, 'SECURE_SSL_REDIRECT', False)
        checks.append(('✅' if ssl_enabled else '⚠️', f'SSL Redirect: {ssl_enabled}'))
        
        # Verificar configuración de archivos estáticos
        static_root = getattr(settings, 'STATIC_ROOT', None)
        if static_root and '/public_html/' in static_root:
            checks.append(('✅', f'STATIC_ROOT configurado para Hostinger: {static_root}'))
        else:
            checks.append(('⚠️', f'STATIC_ROOT no parece configurado para Hostinger: {static_root}'))
        
        # Verificar middleware de Hostinger
        middleware = getattr(settings, 'MIDDLEWARE', [])
        hostinger_middleware = any('hostinger_security' in mw for mw in middleware)
        checks.append(('✅' if hostinger_middleware else '⚠️', f'Middleware Hostinger: {hostinger_middleware}'))
        
        # Verificar configuración de email SMTP
        email_host = getattr(settings, 'EMAIL_HOST', '')
        if 'hostinger.com' in email_host:
            checks.append(('✅', f'Email SMTP Hostinger configurado: {email_host}'))
        else:
            checks.append(('⚠️', f'Email host: {email_host}'))
        
        # Verificar URL secreta de admin
        admin_secret = getattr(settings, 'ADMIN_URL_SECRET', 'admin')
        if admin_secret != 'admin' and len(admin_secret) > 10:
            checks.append(('✅', 'URL secreta de admin configurada'))
        else:
            checks.append(('❌', 'URL secreta de admin NO configurada o insegura'))
        
        # Mostrar resultados
        for status, message in checks:
            self.stdout.write(f'  {status} {message}')
        
        # Recomendaciones específicas
        self.stdout.write('\n💡 RECOMENDACIONES HOSTINGER:')
        self.stdout.write('  📁 Archivos: /home/uXXXXXX/domains/tu-dominio.com/')
        self.stdout.write('  🗄️ Logs: /var/log/nginx/ y ~/domains/tu-dominio.com/logs/')
        self.stdout.write('  🔧 Config Nginx: /etc/nginx/sites-available/tu-dominio.com')
        self.stdout.write('  🔐 SSL: sudo certbot certificates')
        self.stdout.write('  🔥 Firewall: sudo ufw status')

    def _check_production_readiness(self):
        """Verificación completa para producción"""
        self.stdout.write('\n🚀 VERIFICACIÓN DE PRODUCCIÓN COMPLETA:')
        
        critical_checks = []
        
        # Verificaciones críticas
        debug_status = getattr(settings, 'DEBUG', True)
        critical_checks.append(('❌' if debug_status else '✅', f'DEBUG: {debug_status}'))
        
        secret_key = getattr(settings, 'SECRET_KEY', '')
        if len(secret_key) >= 50:
            critical_checks.append(('✅', 'SECRET_KEY: Longitud adecuada'))
        else:
            critical_checks.append(('❌', 'SECRET_KEY: Muy corta o insegura'))
        
        allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
        if '*' in allowed_hosts:
            critical_checks.append(('❌', 'ALLOWED_HOSTS: Permitiendo todos los hosts (inseguro)'))
        elif allowed_hosts:
            critical_checks.append(('✅', f'ALLOWED_HOSTS: {len(allowed_hosts)} hosts configurados'))
        else:
            critical_checks.append(('❌', 'ALLOWED_HOSTS: No configurado'))
        
        # Verificar HTTPS
        ssl_redirect = getattr(settings, 'SECURE_SSL_REDIRECT', False)
        critical_checks.append(('✅' if ssl_redirect else '❌', f'HTTPS obligatorio: {ssl_redirect}'))
        
        # Verificar configuración de seguridad
        security_middleware = any('SecurityMiddleware' in mw for mw in getattr(settings, 'MIDDLEWARE', []))
        critical_checks.append(('✅' if security_middleware else '❌', f'Security Middleware: {security_middleware}'))
        
        # Mostrar verificaciones críticas
        self.stdout.write('\n🔴 VERIFICACIONES CRÍTICAS:')
        all_critical_pass = True
        for status, message in critical_checks:
            self.stdout.write(f'  {status} {message}')
            if status == '❌':
                all_critical_pass = False
        
        if all_critical_pass:
            self.stdout.write(self.style.SUCCESS('\n🎉 ¡TODAS LAS VERIFICACIONES CRÍTICAS PASARON!'))
            self.stdout.write(self.style.SUCCESS('✅ Tu plataforma está lista para producción'))
        else:
            self.stdout.write(self.style.ERROR('\n⚠️ HAY PROBLEMAS CRÍTICOS QUE RESOLVER'))
            self.stdout.write(self.style.ERROR('❌ NO desplegues hasta resolver los errores'))
        
        # Verificaciones adicionales
        self.stdout.write('\n📋 VERIFICACIONES ADICIONALES:')
        
        # Verificar base de datos
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                self.stdout.write('  ✅ Conexión a base de datos funcionando')
        except Exception as e:
            self.stdout.write(f'  ❌ Error de base de datos: {e}')
        
        # Verificar archivos estáticos
        static_root = getattr(settings, 'STATIC_ROOT', None)
        if static_root and os.path.exists(static_root):
            self.stdout.write(f'  ✅ STATIC_ROOT existe: {static_root}')
        else:
            self.stdout.write(f'  ⚠️ STATIC_ROOT no encontrado: {static_root}')
        
        # Verificar logs
        log_dir = getattr(settings, 'LOG_DIR', 'logs')
        if os.path.exists(log_dir):
            log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
            self.stdout.write(f'  ✅ Logs funcionando: {len(log_files)} archivos')
        else:
            self.stdout.write(f'  ⚠️ Directorio de logs no encontrado: {log_dir}')
        
        # Verificar superusuarios
        from django.contrib.auth.models import User
        superusers = User.objects.filter(is_superuser=True)
        if superusers.exists():
            self.stdout.write(f'  ✅ Superusuarios configurados: {superusers.count()}')
        else:
            self.stdout.write('  ❌ No hay superusuarios configurados')
        
        self.stdout.write('\n🛠️ COMANDOS DE DESPLIEGUE:')
        self.stdout.write('  1. python manage.py collectstatic --noinput')
        self.stdout.write('  2. python manage.py migrate')
        self.stdout.write('  3. sudo systemctl restart gunicorn')
        self.stdout.write('  4. sudo systemctl restart nginx')
        self.stdout.write('  5. sudo certbot renew --dry-run')
