#plataforma-cursos/usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'full_name', 'is_email_verified', 'suscrito_newsletter', 'is_staff', 'is_active', 'created_at')
    list_filter = ('is_staff', 'is_active', 'is_email_verified', 'suscrito_newsletter', 'failed_login_attempts')
    search_fields = ('email', 'username', 'full_name')
    actions = ['verify_emails', 'unverify_emails', 'unlock_accounts']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('username', 'full_name', 'phone', 'telegram_id', 'profile_picture')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Seguridad', {'fields': ('is_email_verified', 'suscrito_newsletter', 'failed_login_attempts', 'account_locked_until', 'last_login_ip')}),
        ('Fechas', {'fields': ('last_login', 'created_at', 'updated_at')}),
        ('Datos adicionales', {'fields': ('preferences',), 'classes': ('collapse',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'full_name', 'password1', 'password2', 'is_email_verified', 'suscrito_newsletter'),
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    ordering = ('email',)

    def verify_emails(self, request, queryset):
        """Acción para verificar emails seleccionados"""
        updated = queryset.update(is_email_verified=True, email_verification_token=None)
        self.message_user(request, f'{updated} usuarios marcados como email verificado.')
    verify_emails.short_description = "Marcar emails como verificados"

    def unverify_emails(self, request, queryset):
        """Acción para desverificar emails seleccionados"""
        updated = queryset.update(is_email_verified=False)
        self.message_user(request, f'{updated} usuarios marcados como email no verificado.')
    unverify_emails.short_description = "Marcar emails como no verificados"

    def unlock_accounts(self, request, queryset):
        """Acción para desbloquear cuentas"""
        updated = queryset.update(failed_login_attempts=0, account_locked_until=None)
        self.message_user(request, f'{updated} cuentas desbloqueadas.')
    unlock_accounts.short_description = "Desbloquear cuentas"