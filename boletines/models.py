from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
from django.conf import settings
from blogs.models import BlogPost
from cursos.models import Course
import os


def validate_image_size(image):
    """Validar que la imagen no sea demasiado grande"""
    if image.size > 3 * 1024 * 1024:  # 3MB
        raise ValidationError('La imagen no puede ser mayor a 3MB.')


def upload_boletin_image(instance, filename):
    """Función para generar path seguro para imágenes del boletín"""
    import uuid
    ext = os.path.splitext(filename)[1].lower()
    safe_filename = f"{uuid.uuid4().hex}{ext}"
    return f'boletines/{instance.categoria.lower()}/{safe_filename}'


class Boletin(models.Model):
    """Modelo para boletines informativos"""
    
    CATEGORIA_CHOICES = [
        ('blog', '📰 Blog/Noticias'),
        ('cursos', '🎓 Cursos'),
        ('promociones', '🏷️ Promociones'),
        ('membresias', '💎 Membresías'),
        ('anuncios', '📢 Anuncios'),
        ('eventos', '🎉 Eventos'),
    ]
    
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('programado', 'Programado'),
        ('enviado', 'Enviado'),
        ('cancelado', 'Cancelado'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('normal', 'Normal'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    # Campos básicos
    titulo = models.CharField(max_length=200, help_text="Título del boletín")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    resumen = models.TextField(max_length=300, help_text="Resumen corto para preview")
    contenido = models.TextField(help_text="Contenido principal del boletín")
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='anuncios')
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='normal')
    
    # Imagen destacada
    imagen_destacada = models.ImageField(
        upload_to=upload_boletin_image,
        validators=[validate_image_size],
        blank=True,
        null=True,
        help_text="Imagen opcional para el boletín"
    )
    
    # Relaciones opcionales
    blog_relacionado = models.ForeignKey(
        BlogPost,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Blog que generó este boletín automáticamente"
    )
    
    curso_relacionado = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Curso relacionado con este boletín"
    )
    
    # Estado y programación
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='borrador')
    fecha_programada = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha y hora para envío programado"
    )
    fecha_enviado = models.DateTimeField(null=True, blank=True)
    
    # Segmentación
    solo_suscriptores_premium = models.BooleanField(
        default=False,
        help_text="Enviar solo a usuarios con membresía premium"
    )
      # Metadatos
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='boletines_creados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    # Estadísticas
    total_enviados = models.PositiveIntegerField(default=0)
    total_abiertos = models.PositiveIntegerField(default=0)
    total_clicks = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Boletín'
        verbose_name_plural = 'Boletines'
        indexes = [
            models.Index(fields=['categoria', 'estado']),
            models.Index(fields=['fecha_programada']),
            models.Index(fields=['fecha_creacion']),
        ]
    
    def __str__(self):
        return f"{self.get_categoria_display()} - {self.titulo}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            import uuid
            base_slug = slugify(self.titulo)
            if not base_slug:
                base_slug = f"boletin-{uuid.uuid4().hex[:8]}"
            
            unique_slug = base_slug
            counter = 1
            while Boletin.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('boletines:detalle', kwargs={'slug': self.slug})
    
    def contenido_preview(self):
        """Devuelve una versión limpia del contenido para preview"""
        clean_content = strip_tags(self.contenido)
        return clean_content[:150] + '...' if len(clean_content) > 150 else clean_content
    
    def puede_enviar(self):
        """Verifica si el boletín puede ser enviado"""
        return self.estado in ['borrador', 'programado'] and self.activo
    
    def es_automatico(self):
        """Verifica si es un boletín generado automáticamente"""
        return self.blog_relacionado is not None
    def get_destinatarios_count(self):
        """Cuenta los posibles destinatarios según la segmentación"""
        from usuarios.models import CustomUser
        if self.solo_suscriptores_premium:
            return CustomUser.objects.filter(
                suscrito_newsletter=True,
                memberships__status='active'
            ).distinct().count()
        else:
            return CustomUser.objects.filter(suscrito_newsletter=True).count()


class BoletinSuscriptor(models.Model):
    """Relación entre boletines y suscriptores para tracking"""
    boletin = models.ForeignKey(Boletin, on_delete=models.CASCADE, related_name='suscripciones')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Tracking
    enviado = models.BooleanField(default=False)
    fecha_enviado = models.DateTimeField(null=True, blank=True)
    abierto = models.BooleanField(default=False)
    fecha_abierto = models.DateTimeField(null=True, blank=True)
    clicks = models.PositiveIntegerField(default=0)
    fecha_ultimo_click = models.DateTimeField(null=True, blank=True)
    
    # Error handling
    error_envio = models.TextField(blank=True, null=True)
    intentos_envio = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['boletin', 'usuario']
        verbose_name = 'Suscripción de Boletín'
        verbose_name_plural = 'Suscripciones de Boletines'
        indexes = [
            models.Index(fields=['boletin', 'enviado']),
            models.Index(fields=['usuario', 'abierto']),
        ]
    
    def __str__(self):
        return f"{self.boletin.titulo} → {self.usuario.username}"
    
    def marcar_como_abierto(self):
        """Marca el boletín como abierto por el usuario"""
        if not self.abierto:
            self.abierto = True
            self.fecha_abierto = timezone.now()
            self.save()
            
            # Actualizar estadísticas del boletín
            self.boletin.total_abiertos += 1
            self.boletin.save(update_fields=['total_abiertos'])
    
    def registrar_click(self):
        """Registra un click en el boletín"""
        self.clicks += 1
        self.fecha_ultimo_click = timezone.now()
        self.save()
        
        # Actualizar estadísticas del boletín
        self.boletin.total_clicks += 1
        self.boletin.save(update_fields=['total_clicks'])


class PlantillaBoletin(models.Model):
    """Plantillas predefinidas para diferentes tipos de boletines"""
    
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=20, choices=Boletin.CATEGORIA_CHOICES)
    descripcion = models.TextField(blank=True)
    
    # Plantilla HTML
    html_template = models.TextField(help_text="Template HTML del boletín")
    css_styles = models.TextField(blank=True, help_text="Estilos CSS específicos")
    
    # Configuración
    activa = models.BooleanField(default=True)
    por_defecto = models.BooleanField(default=False)
      # Metadatos
    creada_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['categoria', 'nombre']
        verbose_name = 'Plantilla de Boletín'
        verbose_name_plural = 'Plantillas de Boletines'
        unique_together = ['categoria', 'por_defecto']
    
    def __str__(self):
        return f"{self.get_categoria_display()} - {self.nombre}"
    
    def save(self, *args, **kwargs):
        # Si se marca como por defecto, quitar el flag de otras plantillas de la misma categoría
        if self.por_defecto:
            PlantillaBoletin.objects.filter(
                categoria=self.categoria,
                por_defecto=True
            ).exclude(pk=self.pk).update(por_defecto=False)
        
        super().save(*args, **kwargs)
