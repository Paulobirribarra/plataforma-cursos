from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Boletin, BoletinSuscriptor, PlantillaBoletin


@admin.register(Boletin)
class BoletinAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'categoria_display', 'estado_display', 'prioridad',
        'total_enviados', 'total_abiertos', 'fecha_creacion', 'acciones'
    ]
    list_filter = ['categoria', 'estado', 'prioridad', 'fecha_creacion', 'solo_suscriptores_premium']
    search_fields = ['titulo', 'resumen', 'contenido']
    readonly_fields = ['slug', 'fecha_creacion', 'fecha_actualizacion', 'total_enviados', 'total_abiertos', 'total_clicks']
    date_hierarchy = 'fecha_creacion'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'slug', 'resumen', 'contenido', 'imagen_destacada')
        }),
        ('Categorización', {
            'fields': ('categoria', 'prioridad')
        }),
        ('Relaciones', {
            'fields': ('blog_relacionado', 'curso_relacionado'),
            'classes': ('collapse',)
        }),
        ('Estado y Programación', {
            'fields': ('estado', 'fecha_programada', 'fecha_enviado')
        }),
        ('Segmentación', {
            'fields': ('solo_suscriptores_premium',)
        }),
        ('Metadatos', {
            'fields': ('creado_por', 'fecha_creacion', 'fecha_actualizacion', 'activo'),
            'classes': ('collapse',)
        }),
        ('Estadísticas', {
            'fields': ('total_enviados', 'total_abiertos', 'total_clicks'),
            'classes': ('collapse',)
        })
    )
    
    def categoria_display(self, obj):
        colors = {
            'blog': 'primary',
            'cursos': 'success',
            'promociones': 'warning',
            'membresias': 'info',
            'anuncios': 'secondary',
            'eventos': 'danger'
        }
        color = colors.get(obj.categoria, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_categoria_display()
        )
    categoria_display.short_description = 'Categoría'
    
    def estado_display(self, obj):
        colors = {
            'borrador': 'warning',
            'programado': 'info',
            'enviado': 'success',
            'cancelado': 'danger'
        }
        color = colors.get(obj.estado, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_display.short_description = 'Estado'
    
    def acciones(self, obj):
        buttons = []
        
        # Ver en frontend
        if obj.estado == 'enviado':
            buttons.append(format_html(
                '<a href="{}" class="btn btn-sm btn-outline-primary" target="_blank">Ver</a>',
                obj.get_absolute_url()
            ))
        
        # Enviar (si puede)
        if obj.puede_enviar():
            buttons.append(format_html(
                '<a href="{}" class="btn btn-sm btn-outline-success">Enviar</a>',
                reverse('boletines:admin_enviar', kwargs={'slug': obj.slug})
            ))
        
        # Estadísticas
        if obj.estado == 'enviado' and obj.total_enviados > 0:
            buttons.append(format_html(
                '<a href="{}" class="btn btn-sm btn-outline-info">Stats</a>',
                reverse('boletines:admin_estadisticas', kwargs={'slug': obj.slug})
            ))
        
        return format_html(' '.join(buttons))
    acciones.short_description = 'Acciones'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es nuevo
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'creado_por', 'blog_relacionado', 'curso_relacionado'
        )


@admin.register(BoletinSuscriptor)
class BoletinSuscriptorAdmin(admin.ModelAdmin):
    list_display = [
        'boletin', 'usuario_display', 'enviado', 'abierto',
        'clicks', 'fecha_enviado', 'fecha_abierto'
    ]
    list_filter = ['enviado', 'abierto', 'fecha_enviado', 'boletin__categoria']
    search_fields = ['boletin__titulo', 'usuario__username', 'usuario__email']
    readonly_fields = ['fecha_enviado', 'fecha_abierto', 'fecha_ultimo_click', 'intentos_envio']
    date_hierarchy = 'fecha_enviado'
    
    def usuario_display(self, obj):
        return f"{obj.usuario.get_full_name()} ({obj.usuario.username})"
    usuario_display.short_description = 'Usuario'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('boletin', 'usuario')


@admin.register(PlantillaBoletin)
class PlantillaBoletinAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria_display', 'por_defecto', 'activa', 'fecha_creacion']
    list_filter = ['categoria', 'activa', 'por_defecto', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'categoria', 'descripcion')
        }),
        ('Plantilla', {
            'fields': ('html_template', 'css_styles')
        }),
        ('Configuración', {
            'fields': ('activa', 'por_defecto')
        }),
        ('Metadatos', {
            'fields': ('creada_por', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        })
    )
    
    def categoria_display(self, obj):
        colors = {
            'blog': 'primary',
            'cursos': 'success',
            'promociones': 'warning',
            'membresias': 'info',
            'anuncios': 'secondary',
            'eventos': 'danger'
        }
        color = colors.get(obj.categoria, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_categoria_display()
        )
    categoria_display.short_description = 'Categoría'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es nuevo
            obj.creada_por = request.user
        super().save_model(request, obj, form, change)
    
    class Media:
        css = {
            'all': ('admin/css/forms.css',)
        }
        js = ('admin/js/jquery.init.js', 'admin/js/collapse.js')
