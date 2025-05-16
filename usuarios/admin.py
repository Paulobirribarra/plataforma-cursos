#plataforma-cursos/usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'full_name', 'is_staff', 'created_at')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'username', 'full_name')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('username', 'full_name', 'phone', 'telegram_id', 'preferences')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas', {'fields': ('created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'full_name', 'password1', 'password2'),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('email',)