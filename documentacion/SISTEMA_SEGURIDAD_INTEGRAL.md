# 🔐 Guía de Seguridad para Producción

## 📋 **RESUMEN EJECUTIVO**

Este documento describe el sistema integral de seguridad implementado para proteger el panel de administración y funcionalidades críticas de la plataforma de cursos.

### **✅ CARACTERÍSTICAS DE SEGURIDAD IMPLEMENTADAS:**

1. **Middleware de Seguridad Multinivel**
2. **Decoradores Granulares por Rol**
3. **Rate Limiting Inteligente**
4. **Auditoría y Logging Completo**
5. **Protección de Sesiones Avanzada**
6. **Headers de Seguridad**
7. **Sistema de Alertas**

---

## 🚀 **IMPLEMENTACIÓN RÁPIDA**

### **1. Activar Sistema de Seguridad**

```python
# En plataforma_cursos/settings.py

# Agregar middleware de producción
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    
    # ✅ MIDDLEWARE DE SEGURIDAD INTEGRAL
    "plataforma_cursos.middleware.admin_security.AdminSecurityMiddleware",
    "plataforma_cursos.middleware.production_security.ProductionSecurityMiddleware",
    "plataforma_cursos.middleware.production_security.AdminAccessAuditMiddleware", 
    "plataforma_cursos.middleware.production_security.SessionSecurityMiddleware",
]

# Aplicar configuraciones de seguridad
from plataforma_cursos.security_config import apply_production_security_settings
apply_production_security_settings(locals())
```

### **2. Configurar Variables de Entorno**

```bash
# Copiar archivo de ejemplo
cp .env.production.example .env

# Editar con valores de producción
nano .env
```

**Variables críticas a configurar:**
```bash
# CRÍTICO: Cambiar estos valores
SECRET_KEY=tu-secret-key-super-segura-de-al-menos-50-caracteres
ADMIN_URL_SECRET=tu-url-secreta-admin-impredecible-2024

# Configuración de seguridad
DEBUG=False
ENABLE_RATE_LIMITING=True
ENABLE_SECURITY_EMAIL_ALERTS=True
ADMIN_EMAIL=admin@tu-dominio.com
```

### **3. Ejecutar Auditoría Inicial**

```bash
# Verificar configuración de seguridad
python manage.py security_audit --action=check-config

# Auditoría completa
python manage.py security_audit --action=audit

# Crear usuario admin seguro
python manage.py security_audit --action=create-admin
```

---

## 🛡️ **SISTEMA DE PROTECCIÓN POR NIVELES**

### **NIVEL 1: Middleware de Seguridad Base**
- ✅ Protección CSRF
- ✅ Headers de seguridad (XSS, Clickjacking, etc.)
- ✅ Rate limiting por IP
- ✅ Detección de patrones sospechosos

### **NIVEL 2: Protección de Admin**
- ✅ URL de admin personalizada y secreta
- ✅ Verificación de permisos multinivel
- ✅ Logging de todos los accesos
- ✅ Timeout de sesiones administrativas

### **NIVEL 3: Protección por Roles**
```python
# Decoradores disponibles:
@superuser_required          # Solo superusuarios
@content_manager_required    # Gestión de contenido (blogs, boletines, cursos)
@admin_panel_required        # Acceso al panel de administración
@user_manager_required       # Gestión de usuarios (solo superusers)
```

### **NIVEL 4: Auditoría y Monitoreo**
- ✅ Logs detallados de actividad admin
- ✅ Alertas por email/Slack
- ✅ Tracking de cambios de IP
- ✅ Detección de actividad sospechosa

---

## 🔧 **CONFIGURACIÓN DETALLADA**

### **Rate Limiting**

```python
# Configuración por tipo de endpoint
RATE_LIMITING_CONFIG = {
    'login': {'requests': 5, 'window': 300},      # 5 intentos por 5 min
    'admin': {'requests': 50, 'window': 300},     # 50 requests por 5 min
    'api': {'requests': 100, 'window': 300},      # 100 requests por 5 min
    'general': {'requests': 200, 'window': 300}   # 200 requests por 5 min
}
```

### **Sesiones Seguras**

```python
# Configuración automática en producción
SESSION_COOKIE_SECURE = True        # Solo HTTPS
SESSION_COOKIE_HTTPONLY = True      # No accesible desde JS
SESSION_COOKIE_SAMESITE = 'Lax'     # Protección CSRF
ADMIN_SESSION_TIMEOUT = 1800        # 30 min para admins
```

### **Headers de Seguridad**

```python
# Aplicados automáticamente
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: [configuración detallada]
```

---

## 📊 **MONITOREO Y AUDITORÍA**

### **Comandos de Gestión**

```bash
# Auditoría completa del sistema
python manage.py security_audit

# Verificar solo configuración
python manage.py security_audit --action=check-config

# Resetear intentos de login fallidos
python manage.py security_audit --action=reset-failed-logins

# Bloquear IP sospechosa
python manage.py security_audit --action=block-ip --ip=192.168.1.100 --duration=3600

# Desbloquear IP
python manage.py security_audit --action=unblock-ip --ip=192.168.1.100
```

### **Logs de Seguridad**

```bash
# Ubicación de logs
logs/security.log          # Eventos generales de seguridad
logs/admin_access.log       # Accesos al panel de administración
```

### **Eventos Críticos que Generan Alertas**

- 🚨 Rate limit excedido repetidamente
- 🚨 Actividad sospechosa en admin
- 🚨 Cambio de IP en sesión administrativa
- 🚨 Intentos de acceso a URLs bloqueadas
- 🚨 Acceso de superusuario

---

## 🔐 **MEJORES PRÁCTICAS DE USO**

### **Para Administradores**

1. **Usar URLs secretas:** Nunca acceder por `/admin/`, siempre usar la URL secreta
2. **Sesiones cortas:** Las sesiones admin expiran en 30 minutos
3. **IPs confiables:** Considerar restricción por IP en entornos críticos
4. **Monitoreo regular:** Revisar logs de seguridad semanalmente

### **Para Desarrolladores**

1. **Decoradores apropiados:** Usar el decorador más restrictivo posible
2. **No hardcodear secrets:** Usar variables de entorno siempre
3. **Testing de seguridad:** Probar con usuarios de diferentes roles
4. **Principio de menor privilegio:** Otorgar solo permisos necesarios

### **Para DevOps**

1. **HTTPS obligatorio:** Nunca ejecutar en producción sin HTTPS
2. **Backup de logs:** Mantener logs de seguridad por al menos 90 días
3. **Monitoreo activo:** Configurar alertas para eventos críticos
4. **Actualizaciones:** Mantener dependencies actualizadas

---

## 🚨 **RESPUESTA A INCIDENTES**

### **Si se Detecta Actividad Sospechosa:**

1. **Inmediato:**
   ```bash
   # Bloquear IP sospechosa
   python manage.py security_audit --action=block-ip --ip=[IP_SOSPECHOSA]
   
   # Revisar logs recientes
   tail -f logs/security.log
   ```

2. **Investigación:**
   ```bash
   # Auditoría completa
   python manage.py security_audit
   
   # Revisar sesiones activas
   python manage.py shell
   >>> from django.contrib.sessions.models import Session
   >>> Session.objects.filter(expire_date__gt=timezone.now())
   ```

3. **Recuperación:**
   ```bash
   # Cambiar secrets críticos
   # Forzar logout de todas las sesiones
   # Notificar a usuarios afectados
   ```

### **Escalamiento:**

- **Nivel 1:** Administrador del sistema
- **Nivel 2:** Equipo de seguridad IT
- **Nivel 3:** Consultor de seguridad externo

---

## 📞 **SOPORTE Y CONTACTO**

### **Documentación Adicional:**
- `plataforma_cursos/security_config.py` - Configuración detallada
- `usuarios/decorators.py` - Decoradores de seguridad
- `middleware/production_security.py` - Middleware de protección

### **Testing de Seguridad:**
```bash
# Verificar que el sistema funciona
python manage.py test usuarios.tests.SecurityTestCase
```

### **Actualizaciones:**
- Revisar logs semanalmente
- Actualizar configuraciones según amenazas nuevas
- Capacitar al equipo en mejores prácticas

---

## ✅ **CHECKLIST DE DESPLIEGUE**

- [ ] Variables de entorno configuradas
- [ ] URL de admin cambiada
- [ ] HTTPS habilitado
- [ ] Rate limiting activado
- [ ] Logs configurados
- [ ] Alertas por email configuradas
- [ ] Backup automático configurado
- [ ] Auditoría inicial ejecutada
- [ ] Usuario admin seguro creado
- [ ] Documentación del equipo actualizada

**🎯 Con este sistema, tu plataforma tendrá seguridad de nivel empresarial.**
