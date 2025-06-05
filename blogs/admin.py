from django.contrib import admin
from django.utils.html import format_html
from .models import ContactMessage, BlogPost


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email', 'asunto', 'status_badge', 'fecha_creacion', 'whatsapp_link']
    list_filter = ['status', 'fecha_creacion', 'asunto']
    search_fields = ['nombre', 'email', 'asunto', 'mensaje']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información del Contacto', {
            'fields': ('nombre', 'email', 'telefono')
        }),
        ('Mensaje', {
            'fields': ('asunto', 'mensaje')
        }),
        ('Gestión', {
            'fields': ('status',)
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'nuevo': 'red',
            'revisado': 'orange', 
            'respondido': 'green',
            'cerrado': 'gray'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">● {}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def whatsapp_link(self, obj):
        if obj.telefono:
            # Limpiar número de teléfono (quitar espacios, guiones, etc)
            phone = ''.join(filter(str.isdigit, obj.telefono))
            message = f"Hola {obj.nombre}, recibimos tu consulta sobre: {obj.asunto}"
            url = f"https://wa.me/{phone}?text={message}"
            return format_html('<a href="{}" target="_blank">💬 WhatsApp</a>', url)
        return "-"
    whatsapp_link.short_description = 'WhatsApp'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()
    
    # Acciones en lote
    actions = ['marcar_como_revisado', 'marcar_como_respondido']
    
    def marcar_como_revisado(self, request, queryset):
        updated = queryset.update(status='revisado')
        self.message_user(request, f'{updated} mensajes marcados como revisados.')
    marcar_como_revisado.short_description = "Marcar como revisado"
    
    def marcar_como_respondido(self, request, queryset):
        updated = queryset.update(status='respondido')
        self.message_user(request, f'{updated} mensajes marcados como respondidos.')
    marcar_como_respondido.short_description = "Marcar como respondido"


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria_badge', 'autor', 'fecha_publicacion', 'activo', 'destacado', 'visitas']
    list_filter = ['categoria', 'activo', 'destacado', 'fecha_publicacion', 'autor']
    search_fields = ['titulo', 'contenido', 'resumen']
    list_editable = ['activo', 'destacado']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'visitas', 'tiempo_lectura_display']
    prepopulated_fields = {'slug': ('titulo',)}
    date_hierarchy = 'fecha_publicacion'
    list_per_page = 20
    
    fieldsets = (
        ('Contenido Principal', {
            'fields': ('titulo', 'slug', 'contenido', 'resumen'),
            'description': 'Contenido principal del artículo. El HTML será sanitizado automáticamente.'
        }),
        ('Medios', {
            'fields': ('imagen_destacada',),
            'description': 'Imagen destacada (máximo 5MB, formatos permitidos: JPG, PNG, GIF, WebP)'
        }),
        ('Categorización y Autor', {
            'fields': ('categoria', 'autor', 'fecha_publicacion')
        }),
        ('Configuración de Publicación', {
            'fields': ('activo', 'destacado'),
            'classes': ('wide',)
        }),
        ('SEO y Metadatos', {
            'fields': ('meta_description',),
            'classes': ('collapse',),
            'description': 'Configuración para motores de búsqueda (se genera automáticamente si se deja vacío)'
        }),
        ('Estadísticas (Solo Lectura)', {
            'fields': ('visitas', 'tiempo_lectura_display', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    class Media:
        css = {
            'all': ('admin/css/blog_admin.css',)
        }
        js = ('admin/js/blog_admin.js',)
    
    def save_model(self, request, obj, form, change):
        """Auto-asignar autor si es nuevo post"""
        if not change:  # Si es un nuevo objeto
            obj.autor = request.user
        super().save_model(request, obj, form, change)
    
    def categoria_badge(self, obj):
        colors = {
            'eventos': '#ff6b6b',
            'noticias': '#4ecdc4',
            'resultados': '#45b7d1',
            'proximos_cursos': '#96ceb4',
            'tips': '#ffeaa7',
            'testimonios': '#dda0dd'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            colors.get(obj.categoria, '#6c757d'),
            obj.get_categoria_display()
        )
    categoria_badge.short_description = 'Categoría'
    
    def tiempo_lectura_display(self, obj):
        return f"{obj.tiempo_lectura} min"
    tiempo_lectura_display.short_description = 'Tiempo de lectura'
    
    actions = ['marcar_como_destacado', 'quitar_destacado', 'publicar', 'despublicar']
    
    def marcar_como_destacado(self, request, queryset):
        queryset.update(destacado=True)
        self.message_user(request, f"Se marcaron {queryset.count()} posts como destacados.")
    marcar_como_destacado.short_description = "Marcar como destacado"
    
    def quitar_destacado(self, request, queryset):
        queryset.update(destacado=False)
        self.message_user(request, f"Se quitó el destacado a {queryset.count()} posts.")
    quitar_destacado.short_description = "Quitar destacado"
    
    def publicar(self, request, queryset):
        queryset.update(activo=True)
        self.message_user(request, f"Se publicaron {queryset.count()} posts.")
    publicar.short_description = "Publicar posts"
    
    def despublicar(self, request, queryset):
        queryset.update(activo=False)
        self.message_user(request, f"Se despublicaron {queryset.count()} posts.")
    despublicar.short_description = "Despublicar posts"
