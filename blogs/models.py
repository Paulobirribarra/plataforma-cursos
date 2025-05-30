from django.db import models
from django.utils import timezone

class ContactMessage(models.Model):
    """Modelo para almacenar mensajes de contacto desde el formulario web"""
    
    STATUS_CHOICES = [
        ('nuevo', 'Nuevo'),
        ('revisado', 'Revisado'),
        ('respondido', 'Respondido'),
        ('cerrado', 'Cerrado'),
    ]
    
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    email = models.EmailField(verbose_name="Email")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    asunto = models.CharField(max_length=200, verbose_name="Asunto")
    mensaje = models.TextField(verbose_name="Mensaje")
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='nuevo',
        verbose_name="Estado"
    )
    fecha_creacion = models.DateTimeField(default=timezone.now, verbose_name="Fecha de creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    
    class Meta:
        verbose_name = "Mensaje de Contacto"
        verbose_name_plural = "Mensajes de Contacto"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.nombre} - {self.asunto} ({self.get_status_display()})"
