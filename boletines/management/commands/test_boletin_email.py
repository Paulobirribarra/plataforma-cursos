import os
import sys
import locale
from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from boletines.models import Boletin

# Configurar codificación UTF-8 completamente
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8', errors='replace') if hasattr(sys.stdout, 'reconfigure') else None

class Command(BaseCommand):
    help = 'Envía un boletín de prueba via email usando Gmail SMTP'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default=settings.EMAIL_HOST_USER,
            help='Email de destino para la prueba'
        )
        parser.add_argument(
            '--boletin-id',
            type=int,
            default=None,
            help='ID del boletín a enviar (por defecto usa el último)'
        )

    def handle(self, *args, **options):
        email_destino = options['email']
        boletin_id = options['boletin_id']

        try:
            # Obtener el boletín
            if boletin_id:
                try:
                    boletin = Boletin.objects.get(id=boletin_id)
                except Boletin.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'No se encontró el boletín con ID {boletin_id}'))
                    return
            else:
                boletin = Boletin.objects.last()
                if not boletin:
                    self.stdout.write(self.style.ERROR('No hay boletines disponibles en la base de datos'))
                    return

            self.stdout.write(f'Enviando boletín: "{boletin.titulo}" a {email_destino}')

            # Crear contenido del email completamente en inglés para evitar problemas de codificación
            # Mapear estados en español a inglés
            estado_map = {
                'borrador': 'Draft',
                'programado': 'Scheduled', 
                'enviado': 'Sent',
                'cancelado': 'Cancelled'
            }
            
            # Mapear categorías en español a inglés
            categoria_map = {
                'blog': 'Blog/News',
                'cursos': 'Courses',
                'promociones': 'Promotions',
                'membresias': 'Memberships',
                'anuncios': 'Announcements',
                'eventos': 'Events'
            }

            estado_en = estado_map.get(boletin.estado, boletin.estado)
            categoria_en = categoria_map.get(boletin.categoria, boletin.categoria)

            # Crear contenido HTML completamente en inglés
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Newsletter Test</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0;">
    <div style="max-width: 600px; margin: 0 auto; background: #f8f9fa; padding: 20px;">
        <header style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px;">
            <h1 style="margin: 0; font-size: 28px; font-weight: bold;">Newsletter Test</h1>
            <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Advisory Future LTD - Course Platform</p>
        </header>
        
        <main style="background: white; padding: 40px; border-radius: 10px; margin-top: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="color: #667eea; border-bottom: 2px solid #e9ecef; padding-bottom: 15px; margin-bottom: 25px; font-size: 24px;">
                {boletin.titulo}
            </h2>
            
            <div style="margin: 25px 0; font-size: 16px; line-height: 1.7;">
                {boletin.contenido}
            </div>
            
            <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin-top: 35px; border-left: 4px solid #1565c0;">
                <h3 style="margin: 0 0 15px 0; color: #1565c0; font-size: 18px;">Newsletter Information</h3>
                <table style="width: 100%; font-size: 14px; color: #333;">
                    <tr><td style="padding: 5px 0; width: 120px;"><strong>Created by:</strong></td><td style="padding: 5px 0;">{boletin.creado_por.get_full_name() or boletin.creado_por.username}</td></tr>
                    <tr><td style="padding: 5px 0;"><strong>Date:</strong></td><td style="padding: 5px 0;">{boletin.fecha_creacion.strftime('%B %d, %Y at %H:%M')}</td></tr>
                    <tr><td style="padding: 5px 0;"><strong>Status:</strong></td><td style="padding: 5px 0;">{estado_en}</td></tr>
                    <tr><td style="padding: 5px 0;"><strong>Category:</strong></td><td style="padding: 5px 0;">{categoria_en}</td></tr>
                </table>
            </div>
            
            <div style="background: #d4edda; padding: 20px; border-radius: 8px; margin-top: 25px; text-align: center; border: 1px solid #c3e6cb;">
                <p style="margin: 0; font-size: 16px; font-weight: bold; color: #155724;">✅ SMTP Configuration Test Successful!</p>
                <p style="margin: 10px 0 0 0; font-size: 14px; color: #155724;">This email was sent using Gmail SMTP configuration.</p>
            </div>
        </main>
        
        <footer style="text-align: center; padding: 30px 20px; color: #6c757d; font-size: 12px;">
            <p style="margin: 0 0 10px 0; font-weight: bold;">Advisory Future LTD</p>
            <p style="margin: 0;">Course Platform - Newsletter System</p>
            <p style="margin: 10px 0 0 0;">© 2024 All rights reserved</p>
        </footer>
    </div>
</body>
</html>
"""

            # Crear contenido de texto plano
            text_content = f"""
NEWSLETTER TEST - ADVISORY FUTURE LTD
====================================

{boletin.titulo}
{'=' * len(boletin.titulo)}

{boletin.contenido}

NEWSLETTER INFORMATION:
- Created by: {boletin.creado_por.get_full_name() or boletin.creado_por.username}
- Date: {boletin.fecha_creacion.strftime('%B %d, %Y at %H:%M')}
- Status: {estado_en}
- Category: {categoria_en}

SMTP CONFIGURATION TEST SUCCESSFUL
This email was sent from the newsletter system using Gmail SMTP.

Advisory Future LTD - Course Platform
© 2024 All rights reserved
"""

            # Crear asunto completamente en inglés
            subject = f"[TEST] {boletin.titulo} - Advisory Future LTD Newsletter"

            # Crear y enviar el email
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[email_destino]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)

            # Mostrar resultados exitosos
            self.stdout.write(self.style.SUCCESS('✅ Email de prueba enviado exitosamente!'))
            self.stdout.write(self.style.SUCCESS(f'📧 Destinatario: {email_destino}'))
            self.stdout.write(self.style.SUCCESS(f'📰 Boletín: "{boletin.titulo}" (ID: {boletin.id})'))
            self.stdout.write(self.style.SUCCESS(f'🔧 SMTP: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}'))
            self.stdout.write(self.style.SUCCESS(f'📊 Estado: {estado_en} ({boletin.estado})'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error enviando email: {str(e)}'))
            import traceback
            self.stdout.write(self.style.ERROR(f'Detalles del error: {traceback.format_exc()}'))