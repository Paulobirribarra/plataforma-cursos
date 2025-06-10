from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from blogs.models import BlogPost
from cursos.models import Course
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


@receiver(post_save, sender=Course)
def crear_boletin_curso_automatico(sender, instance, created, **kwargs):
    """
    Crear automáticamente un boletín cuando se crea un nuevo curso
    """
    # Solo crear boletín si es un curso nuevo, está disponible y no existe ya un boletín para este curso
    if created and instance.is_available and not Boletin.objects.filter(curso_relacionado=instance).exists():
        try:
            # Crear contenido del boletín basado en el curso
            contenido_boletin = f"""
            <h2>🎓 ¡Nuevo curso disponible!</h2>
            <p>Nos complace anunciar el lanzamiento de nuestro nuevo curso:</p>
            
            <h3>{instance.title}</h3>
            
            <p><strong>Descripción:</strong></p>
            <p>{instance.description[:400]}{'...' if len(instance.description) > 400 else ''}</p>
            
            <p><strong>Detalles del curso:</strong></p>
            <ul>
                <li>🕐 Duración: {instance.duration} horas</li>
                <li>📚 Categoría: {instance.category.name}</li>
                <li>💰 Precio: {'Gratis' if instance.is_free else f'${instance.base_price:,} CLP'}</li>
            </ul>
            
            <p><strong>¿Te interesa este curso?</strong> ¡No esperes más y únete a miles de estudiantes que ya están aprendiendo con nosotros!</p>
            
            <hr>
            
            <p>¡Gracias por ser parte de nuestra comunidad de aprendizaje!</p>
            <p><em>Equipo de Plataforma Cursos</em></p>
            """
            
            # Crear el boletín automático
            boletin = Boletin.objects.create(
                titulo=f"Nuevo curso: {instance.title}",
                resumen=f"Descubre nuestro nuevo curso: {instance.title} en {instance.category.name}",
                contenido=contenido_boletin,
                categoria='cursos',
                curso_relacionado=instance,
                creado_por=instance.created_by,
                prioridad='normal',
                estado='borrador',  # Se crea como borrador para revisión
                activo=True
            )
            
            print(f"✅ Boletín de curso automático creado: {boletin.titulo}")
            
        except Exception as e:
            print(f"❌ Error al crear boletín de curso automático: {str(e)}")
