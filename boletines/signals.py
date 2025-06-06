from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from blogs.models import BlogPost
from .models import Boletin


@receiver(post_save, sender=BlogPost)
def crear_boletin_automatico(sender, instance, created, **kwargs):
    """
    Crear automáticamente un boletín cuando se publica un blog post
    """
    # Solo crear boletín si el blog está activo y no existe ya un boletín para este blog
    if instance.activo and not Boletin.objects.filter(blog_relacionado=instance).exists():
        try:
            # Crear contenido del boletín basado en el blog
            contenido_boletin = f"""
            <h2>🆕 Nuevo artículo en nuestro blog</h2>
            <p>Hemos publicado un nuevo artículo que creemos te interesará:</p>
            
            <h3>{instance.titulo}</h3>
            
            {instance.contenido[:500]}{'...' if len(instance.contenido) > 500 else ''}
            
            <p><strong>¿Te interesa leer más?</strong> Visita nuestro blog para el artículo completo.</p>
            
            <hr>
            
            <p>¡Gracias por ser parte de nuestra comunidad de aprendizaje!</p>
            <p><em>Equipo de Plataforma Cursos</em></p>
            """
            
            # Crear el boletín automático
            boletin = Boletin.objects.create(
                titulo=f"Nuevo artículo: {instance.titulo}",
                resumen=f"Descubre nuestro último artículo del blog: {instance.titulo}",
                contenido=contenido_boletin,
                categoria='blog',
                blog_relacionado=instance,
                creado_por=instance.autor,
                prioridad='normal',
                estado='borrador',  # Se crea como borrador para revisión
                activo=True
            )
            
            print(f"✅ Boletín automático creado: {boletin.titulo}")
            
        except Exception as e:
            print(f"❌ Error al crear boletín automático: {str(e)}")
