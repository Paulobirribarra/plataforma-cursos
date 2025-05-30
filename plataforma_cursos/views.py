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
    """Vista para manejar el formulario de contacto"""
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.POST.get('nombre', '').strip()
        email = request.POST.get('email', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        asunto = request.POST.get('asunto', '').strip()
        mensaje = request.POST.get('mensaje', '').strip()
        
        # Validaciones básicas
        errors = []
        if not nombre:
            errors.append('El nombre es requerido.')
        if not email:
            errors.append('El email es requerido.')
        if not asunto:
            errors.append('El asunto es requerido.')
        if not mensaje:
            errors.append('El mensaje es requerido.')
            
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                # Guardar en la base de datos
                from blogs.models import ContactMessage
                contact_message = ContactMessage.objects.create(
                    nombre=nombre,
                    email=email,
                    telefono=telefono,
                    asunto=asunto,
                    mensaje=mensaje
                )
                
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
                
                # Comentado por ahora - descomentar cuando tengas SMTP configurado
                # send_mail(
                #     email_subject,
                #     email_body,
                #     email,
                #     [settings.DEFAULT_FROM_EMAIL],
                #     fail_silently=False,
                # )
                
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