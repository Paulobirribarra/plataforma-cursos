# Configuración de Email Gmail SMTP

## Configuración exitosa para envío de boletines

### Pasos para configurar Gmail SMTP:

1. **Habilitar autenticación de 2 factores** en tu cuenta de Gmail
2. **Generar contraseña de aplicación**:
   - Ve a tu cuenta de Google → Seguridad
   - En "Acceso a Google", selecciona "Contraseñas de aplicaciones"
   - Genera una nueva contraseña de aplicación para "Correo"
3. **Configurar variables de entorno** en tu archivo `.env`:
   ```
   EMAIL_HOST_USER=tu_email@gmail.com
   EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicación_generada
   CONTACT_EMAIL=tu_email@gmail.com
   ```

### Configuración en settings.py:

```python
# Configuración de correo (SMTP GMAIL - ACTIVO)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('EMAIL_HOST_USER')
CONTACT_EMAIL = config('CONTACT_EMAIL', default='contact@yoursite.com')

# Configuración de codificación para emails
DEFAULT_CHARSET = 'utf-8'
FILE_CHARSET = 'utf-8'
```

### Problemas resueltos:

1. **Error de codificación ASCII**: Eliminación de variables de entorno del sistema que contenían caracteres especiales
2. **Conflicto entre archivos .env**: Eliminación de archivo `.env.example` durante desarrollo
3. **Variables de entorno del sistema**: Usar `Remove-Item Env:EMAIL_HOST_USER` para limpiar variables conflictivas

### Comando de prueba:

```bash
python manage.py test_boletin_email --boletin-id=ID_DEL_BOLETIN
```

### Estado del sistema:
- ✅ SMTP Gmail configurado y funcionando
- ✅ Codificación UTF-8 para caracteres especiales
- ✅ Templates HTML y texto para emails
- ✅ Envío de boletines completamente operativo
- ✅ Soporte para 3 tipos de envío: prueba, inmediato, programado
