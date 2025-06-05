from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
import os


def validate_image_size(image):
    """Validar que la imagen no sea demasiado grande"""
    if image.size > 5 * 1024 * 1024:  # 5MB
        raise ValidationError('La imagen no puede ser mayor a 5MB.')


def validate_image_extension(image):
    """Validar que la imagen tenga una extensión permitida"""
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    ext = os.path.splitext(image.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(f'Extensión no permitida. Usa: {", ".join(allowed_extensions)}')


def upload_blog_image(instance, filename):
    """Función para generar path seguro para imágenes del blog"""
    # Sanitizar el nombre del archivo
    import uuid
    import os
    ext = os.path.splitext(filename)[1].lower()
    safe_filename = f"{uuid.uuid4().hex}{ext}"
    return f'blog/imagenes/{timezone.now().year}/{timezone.now().month:02d}/{safe_filename}'


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


class BlogPost(models.Model):
    """Modelo para publicaciones del blog"""
    
    CATEGORIA_CHOICES = [
        ('eventos', 'Eventos'),
        ('noticias', 'Noticias'),
        ('resultados', 'Resultados'),
        ('proximos_cursos', 'Próximos Cursos'),
        ('tips', 'Tips y Consejos'),
        ('testimonios', 'Testimonios'),
    ]
    
    titulo = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(max_length=250, unique=True, blank=True, verbose_name="URL amigable")
    contenido = models.TextField(verbose_name="Contenido")
    resumen = models.TextField(max_length=300, blank=True, help_text="Resumen corto para mostrar en listados", verbose_name="Resumen")
    imagen_destacada = models.ImageField(
        upload_to=upload_blog_image,
        blank=True, 
        null=True,
        help_text="Imagen principal del post (máximo 5MB, formatos: JPG, PNG, GIF, WebP)",
        verbose_name="Imagen destacada",
        validators=[validate_image_size, validate_image_extension]
    )
    categoria = models.CharField(
        max_length=20, 
        choices=CATEGORIA_CHOICES, 
        default='noticias',
        verbose_name="Categoría"
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        verbose_name="Autor"
    )
    fecha_publicacion = models.DateTimeField(default=timezone.now, verbose_name="Fecha de publicación")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    activo = models.BooleanField(default=True, verbose_name="Publicado")
    destacado = models.BooleanField(default=False, help_text="Marcar para mostrar en página principal", verbose_name="Destacado")
    meta_description = models.CharField(
        max_length=160, 
        blank=True, 
        help_text="Descripción para SEO (máximo 160 caracteres)",
        verbose_name="Meta descripción"
    )
    visitas = models.PositiveIntegerField(default=0, verbose_name="Número de visitas")
    
    class Meta:
        verbose_name = "Publicación del Blog"
        verbose_name_plural = "Publicaciones del Blog"
        ordering = ['-fecha_publicacion']
        indexes = [
            models.Index(fields=['-fecha_publicacion']),
            models.Index(fields=['categoria']),
            models.Index(fields=['activo']),
        ]
    
    def __str__(self):
        return self.titulo
    def save(self, *args, **kwargs):
        """Auto-generar slug si no existe y sanitizar contenido"""
        # Limpiar contenido HTML peligroso
        import bleach
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                       'ul', 'ol', 'li', 'blockquote', 'a', 'img']
        allowed_attributes = {
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'title', 'width', 'height']
        }
        
        # Sanitizar el contenido si se permite HTML
        if hasattr(bleach, 'clean'):
            self.contenido = bleach.clean(
                self.contenido, 
                tags=allowed_tags, 
                attributes=allowed_attributes,
                strip=True
            )
        
        if not self.slug:
            self.slug = slugify(self.titulo)
            # Asegurar que el slug sea único
            original_slug = self.slug
            counter = 1
            while BlogPost.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        # Auto-generar resumen si no existe
        if not self.resumen:
            # Usar strip_tags para el resumen (sin HTML)
            clean_content = strip_tags(self.contenido)
            self.resumen = clean_content[:250] + "..." if len(clean_content) > 250 else clean_content
        
        # Auto-generar meta_description si no existe
        if not self.meta_description:
            clean_resumen = strip_tags(self.resumen) if self.resumen else strip_tags(self.contenido)
            self.meta_description = clean_resumen[:160]
            
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """URL para ver el post individual"""
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
    
    def incrementar_visitas(self):
        """Incrementar contador de visitas"""
        self.visitas += 1
        self.save(update_fields=['visitas'])
    
    @property
    def tiempo_lectura(self):
        """Estimar tiempo de lectura en minutos"""
        palabras = len(self.contenido.split())
        return max(1, palabras // 200)  # ~200 palabras por minuto
    
    def posts_relacionados(self, limite=3):
        """Obtener posts relacionados por categoría"""
        return BlogPost.objects.filter(
            categoria=self.categoria,
            activo=True
        ).exclude(id=self.id).order_by('-fecha_publicacion')[:limite]
