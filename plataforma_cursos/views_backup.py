# plataforma_cursos/views.py
from django.shortcuts import render
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'home.html')

def nosotros(request):
    return render(request, 'nosotros.html')

def contacto(request):
    """Vista para manejar el formulario de contacto con validaciones robustas"""
    from blogs.forms import ContactForm
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                # Guardar en la base de datos (ya validado y limpio)
                contact_message = form.save()
                
                # Enviar email (opcional, requiere configuración SMTP)
                email_subject = f"Contacto desde la web: {asunto}"
                email_body = f"""
                Nuevo mensaje de contacto:
                
                Nombre: {nombre}
                Email: {email}
                Teléfono: {telefono}
                Asunto: {asunto}
                
                Mensaje:
                {mensaje}
                
                ---------------
                ID del mensaje: {contact_message.id}
                Fecha: {contact_message.fecha_creacion}
                """
                  # Enviar notificación por email
                try:
                    send_mail(
                        email_subject,
                        email_body,
                        settings.DEFAULT_FROM_EMAIL,
                        [settings.CONTACT_EMAIL],  # Email donde recibirás las notificaciones
                        fail_silently=False,
                    )
                except Exception as e:
                    logger.error(f"Error enviando email de contacto: {e}")
                
                # Log del mensaje para desarrollo
                logger.info(f"Mensaje de contacto #{contact_message.id} recibido de {email}: {asunto}")
                
                messages.success(
                    request, 
                    '¡Gracias por contactarnos! Hemos recibido tu mensaje y te responderemos pronto.'
                )
                
                # Limpiar el formulario después del envío exitoso
                return render(request, 'contacto.html', {'form_sent': True})
                
            except Exception as e:
                logger.error(f"Error al procesar formulario de contacto: {e}")
                messages.error(
                    request, 
                    'Hubo un error al enviar tu mensaje. Por favor, inténtalo de nuevo.'
                )
    
    return render(request, 'contacto.html')