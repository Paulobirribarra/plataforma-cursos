"""
Sistema de alertas de seguridad por email
Envía notificaciones automáticas para eventos críticos
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from datetime import datetime, timedelta
from decouple import config

class SecurityAlertManager:
    """
    Gestor de alertas de seguridad automáticas
    """
    
    def __init__(self):
        self.logger = logging.getLogger('plataforma_cursos.middleware.production_security')
        self.alert_threshold = {
            'failed_logins': 5,  # 5 intentos fallidos consecutivos
            'suspicious_activity': 3,  # 3 actividades sospechosas
            'rate_limit_violations': 10,  # 10 violaciones de rate limiting
            'admin_access_anomaly': 1,  # Cualquier acceso anómalo a admin
        }
        
    def send_security_alert(self, alert_type, details, severity='medium'):
        """
        Enviar alerta de seguridad por email
        
        Args:
            alert_type (str): Tipo de alerta (failed_login, suspicious_activity, etc.)
            details (dict): Detalles del evento
            severity (str): Nivel de severidad (low, medium, high, critical)
        """
        if not self._should_send_alert(alert_type, severity):
            return
            
        try:
            # Preparar datos del email
            context = {
                'alert_type': alert_type,
                'severity': severity.upper(),
                'details': details,
                'timestamp': datetime.now(),
                'server_info': {
                    'debug_mode': settings.DEBUG,
                    'allowed_hosts': settings.ALLOWED_HOSTS,
                },
                'incident_id': f"SEC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
            
            # Generar subject dinámico
            subject_map = {
                'failed_login': f"🚨 [{severity.upper()}] Intentos de login fallidos detectados",
                'suspicious_activity': f"⚠️ [{severity.upper()}] Actividad sospechosa detectada", 
                'rate_limit_violation': f"🛑 [{severity.upper()}] Violaciones de rate limiting",
                'admin_access_anomaly': f"🔴 [{severity.upper()}] Acceso anómalo al panel de administración",
                'security_breach': f"🚨 [CRÍTICO] Posible brecha de seguridad detectada",
            }
            
            subject = subject_map.get(alert_type, f"🔔 [{severity.upper()}] Evento de seguridad")
            
            # Crear mensaje HTML
            html_message = self._create_alert_html(context)
            
            # Crear mensaje de texto plano
            text_message = self._create_alert_text(context)
            
            # Enviar email
            self._send_email(subject, text_message, html_message)
            
            # Log del envío
            self.logger.info(f"Alerta de seguridad enviada: {alert_type} - Severidad: {severity}")
            
        except Exception as e:
            self.logger.error(f"Error enviando alerta de seguridad: {str(e)}")
    
    def _should_send_alert(self, alert_type, severity):
        """
        Determinar si se debe enviar la alerta basado en configuración
        """
        # No enviar en desarrollo a menos que sea crítico
        if settings.DEBUG and severity != 'critical':
            return False
            
        # Verificar si las alertas están habilitadas
        return config('SECURITY_ALERTS_ENABLED', default=True, cast=bool)
    
    def _create_alert_html(self, context):
        """
        Crear mensaje HTML para la alerta
        """
        severity_colors = {
            'LOW': '#28a745',
            'MEDIUM': '#ffc107', 
            'HIGH': '#fd7e14',
            'CRITICAL': '#dc3545'
        }
        
        severity_color = severity_colors.get(context['severity'], '#6c757d')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Alerta de Seguridad</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; }}
                .header {{ background-color: {severity_color}; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .footer {{ background-color: #6c757d; color: white; padding: 15px; text-align: center; font-size: 12px; }}
                .status-badge {{ display: inline-block; padding: 5px 10px; border-radius: 15px; color: white; background-color: {severity_color}; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Alerta de Seguridad</h1>
                    <div class="status-badge">{context['severity']}</div>
                </div>
                <div class="content">
                    <h2>Tipo de Evento: {context['alert_type'].replace('_', ' ').title()}</h2>
                    <p><strong>Timestamp:</strong> {context['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>ID del Incidente:</strong> {context['incident_id']}</p>
                    
                    <div class="details">
                        <h3>Detalles del Evento:</h3>
                        <ul>
        """
        
        for key, value in context['details'].items():
            html += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>"
        
        html += f"""
                        </ul>
                    </div>
                    
                    <div class="details">
                        <h3>Información del Servidor:</h3>
                        <ul>
                            <li><strong>Modo Debug:</strong> {'🔴 Activo' if context['server_info']['debug_mode'] else '🟢 Inactivo'}</li>
                            <li><strong>Hosts Permitidos:</strong> {', '.join(context['server_info']['allowed_hosts'])}</li>
                        </ul>
                    </div>
                    
                    <h3>🛡️ Acciones Recomendadas:</h3>
                    <ul>
                        <li>Revisar logs de seguridad inmediatamente</li>
                        <li>Verificar accesos recientes al sistema</li>
                        <li>Monitorear actividad durante las próximas horas</li>
                        {"<li><strong>CRÍTICO:</strong> Considerar bloquear IPs sospechosas</li>" if context['severity'] == 'CRITICAL' else ""}
                    </ul>
                </div>
                <div class="footer">
                    <p>Esta es una alerta automática del sistema de seguridad de la plataforma de cursos.</p>
                    <p>Para más información, revise los logs del sistema o contacte al administrador.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_alert_text(self, context):
        """
        Crear mensaje de texto plano para la alerta
        """
        text = f"""
🔐 ALERTA DE SEGURIDAD - {context['severity']}

Tipo de Evento: {context['alert_type'].replace('_', ' ').title()}
Timestamp: {context['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
ID del Incidente: {context['incident_id']}

DETALLES DEL EVENTO:
"""
        
        for key, value in context['details'].items():
            text += f"- {key.replace('_', ' ').title()}: {value}\n"
            
        text += f"""
INFORMACIÓN DEL SERVIDOR:
- Modo Debug: {'ACTIVO (INSEGURO)' if context['server_info']['debug_mode'] else 'INACTIVO'}
- Hosts Permitidos: {', '.join(context['server_info']['allowed_hosts'])}

ACCIONES RECOMENDADAS:
✓ Revisar logs de seguridad inmediatamente
✓ Verificar accesos recientes al sistema
✓ Monitorear actividad durante las próximas horas
{"✓ CRÍTICO: Considerar bloquear IPs sospechosas" if context['severity'] == 'CRITICAL' else ""}

Esta es una alerta automática del sistema de seguridad.
Para más información, revise los logs del sistema.
        """
        
        return text
    
    def _send_email(self, subject, text_message, html_message):
        """
        Enviar email usando configuración de Django
        """
        admin_emails = config('SECURITY_ALERT_EMAILS', default='admin@example.com').split(',')
        admin_emails = [email.strip() for email in admin_emails]
        
        try:
            from django.core.mail import EmailMultiAlternatives
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=admin_emails
            )
            msg.attach_alternative(html_message, "text/html")
            msg.send()
            
        except Exception as e:
            # Fallback a send_mail básico
            send_mail(
                subject=subject,
                message=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                fail_silently=False,
            )

# Instancia global del gestor de alertas
alert_manager = SecurityAlertManager()

def send_failed_login_alert(ip_address, username, attempt_count):
    """
    Enviar alerta por intentos fallidos de login
    """
    severity = 'high' if attempt_count >= 10 else 'medium' if attempt_count >= 5 else 'low'
    
    alert_manager.send_security_alert(
        alert_type='failed_login',
        details={
            'ip_address': ip_address,
            'username': username,
            'attempt_count': attempt_count,
            'time_window': '5 minutos'
        },
        severity=severity
    )

def send_suspicious_activity_alert(ip_address, activity_details):
    """
    Enviar alerta por actividad sospechosa
    """
    alert_manager.send_security_alert(
        alert_type='suspicious_activity',
        details={
            'ip_address': ip_address,
            'activity_type': activity_details.get('type', 'Unknown'),
            'description': activity_details.get('description', 'Actividad sospechosa detectada'),
            'user_agent': activity_details.get('user_agent', 'Unknown')
        },
        severity='medium'
    )

def send_admin_access_alert(user, ip_address, anomaly_reason):
    """
    Enviar alerta por acceso anómalo al panel de administración
    """
    alert_manager.send_security_alert(
        alert_type='admin_access_anomaly',
        details={
            'username': user.username,
            'email': user.email,
            'ip_address': ip_address,
            'anomaly_reason': anomaly_reason,
            'user_last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Nunca'
        },
        severity='high'
    )

def send_critical_security_alert(threat_type, details):
    """
    Enviar alerta crítica de seguridad
    """
    alert_manager.send_security_alert(
        alert_type='security_breach',
        details=details,
        severity='critical'
    )
