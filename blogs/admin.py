from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email', 'asunto', 'status', 'fecha_creacion']
    list_filter = ['status', 'fecha_creacion', 'asunto']
    search_fields = ['nombre', 'email', 'asunto', 'mensaje']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    list_editable = ['status']
    
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
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()
