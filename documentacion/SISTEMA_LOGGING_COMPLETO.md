# 📊 Sistema de Logging Inteligente - Guía Completa

## 📋 **RESUMEN EJECUTIVO**

El sistema de logging está diseñado para un entorno de **bajo a medio tráfico**, con gestión automática de almacenamiento, rotación inteligente y categorización por criticidad. **NO registra todos los movimientos**, solo eventos relevantes para seguridad, errores y administración.

---

## 🎯 **¿QUÉ SE REGISTRA Y QUÉ NO?**

### ✅ **SE REGISTRA:**

#### 🔐 **Eventos de Seguridad** (`security.log`)
- Intentos de login (exitosos/fallidos)
- Uso de decoradores de permisos (`@superuser_required`, etc.)
- Accesos a URLs restringidas
- Rate limiting y bloqueos de IP
- Cambios en permisos de usuario
- Intentos de acceso no autorizado

#### 🛡️ **Accesos Administrativos** (`admin_access.log`)
- Entrada/salida del panel de administración
- Operaciones CRUD en modelos críticos
- Cambios de configuración
- Sesiones administrativas iniciadas/cerradas

#### ⚠️ **Errores de Aplicación** (`errors.log`)
- Errores HTTP (404, 500, etc.)
- Excepciones no manejadas
- Fallos de base de datos
- Errores de integración con APIs externas

#### 📱 **Eventos de Aplicación** (`application.log`)
- Operaciones de boletines (suscripciones)
- Procesos de pagos importantes
- Cambios en cursos y membresías
- Tareas programadas

#### 🚨 **Eventos Críticos** (`critical.log`)
- Fallos críticos del sistema
- Errores de seguridad graves
- Problemas de integridad de datos
- Alertas que requieren intervención inmediata

### ❌ **NO SE REGISTRA:**

- ✗ Navegación normal de usuarios
- ✗ Todas las peticiones HTTP
- ✗ Consultas rutinarias a la base de datos
- ✗ Carga de páginas públicas
- ✗ Visualización de contenido público
- ✗ Búsquedas normales
- ✗ Movimientos cotidianos sin importancia

---

## 🔄 **SISTEMA DE ROTACIÓN AUTOMÁTICA**

### **Por Tiempo (TimedRotatingFileHandler)**

| Archivo | Rotación | Retención | Descripción |
|---------|----------|-----------|-------------|
| `security.log` | Diaria (medianoche) | 30 días | Eventos de seguridad |
| `admin_access.log` | Semanal (lunes) | 4 semanas | Accesos administrativos |
| `application.log` | Diaria (medianoche) | 7 días | Logs generales |

**Ejemplo de archivos generados:**
```
security.log           <- Archivo actual
security.log.2024-06-01  <- 1 día atrás
security.log.2024-06-02  <- 2 días atrás
...
security.log.2024-05-01  <- Se elimina automáticamente después de 30 días
```

### **Por Tamaño (RotatingFileHandler)**

| Archivo | Tamaño Máximo | Archivos de Respaldo | Total Máximo |
|---------|---------------|---------------------|--------------|
| `errors.log` | 5 MB | 10 archivos | 50 MB |
| `critical.log` | 10 MB | 50 archivos | 500 MB |

**Ejemplo de archivos por tamaño:**
```
errors.log      <- Archivo actual
errors.log.1    <- Respaldo más reciente (5MB)
errors.log.2    <- Respaldo anterior (5MB)
...
errors.log.10   <- Se elimina cuando se crea .11
```

---

## 🎛️ **CONFIGURACIÓN POR AMBIENTE**

### **Desarrollo (DEBUG=True)**
```
📁 logs/
  ├── security.log     (Sin rotación, archivo único)
  ├── errors.log       (Sin rotación, archivo único)
  └── [Logs en consola visible]
```

### **Producción - Bajo Tráfico (DEBUG=False)**
```
📁 logs/
  ├── security.log + archivos rotados (30 días)
  ├── admin_access.log + archivos rotados (4 semanas)
  ├── application.log + archivos rotados (7 días)
  ├── errors.log + archivos rotados (10 x 2.5MB = 25MB)
  └── critical.log + archivos rotados (50 x 5MB = 250MB)
```

### **Producción - Alto Tráfico (low_traffic=False)**
```
📁 logs/
  ├── security.log + archivos rotados (30 días)
  ├── admin_access.log + archivos rotados (4 semanas)
  ├── application.log + archivos rotados (7 días)
  ├── errors.log + archivos rotados (10 x 5MB = 50MB)
  └── critical.log + archivos rotados (50 x 10MB = 500MB)
```

---

## 📏 **ESTIMACIÓN DE ESPACIO EN DISCO**

### **Para un sitio de bajo tráfico (< 1000 usuarios/día):**

| Categoría | Espacio Estimado | Descripción |
|-----------|------------------|-------------|
| Security | 50-100 MB/mes | Logins, permisos, rate limiting |
| Admin Access | 10-20 MB/mes | Panel administrativo |
| Application | 20-50 MB/mes | Operaciones de aplicación |
| Errors | 25 MB máximo | Rotación por tamaño |
| Critical | 250 MB máximo | Solo eventos críticos |

**Total estimado: 355-445 MB máximo**

### **Para un sitio de medio tráfico (1000-10000 usuarios/día):**

| Categoría | Espacio Estimado | Descripción |
|-----------|------------------|-------------|
| Security | 200-500 MB/mes | Más actividad de seguridad |
| Admin Access | 50-100 MB/mes | Más administración |
| Application | 100-300 MB/mes | Más operaciones |
| Errors | 50 MB máximo | Rotación por tamaño |
| Critical | 500 MB máximo | Más eventos críticos |

**Total estimado: 900-1450 MB máximo**

---

## 🔧 **COMANDOS DE GESTIÓN**

### **Verificar Estado de Logs**
```bash
# Estadísticas completas
python manage.py security_audit --action=log-stats

# Ver tamaño de archivos
ls -lh logs/

# Contar líneas en logs activos
wc -l logs/*.log
```

### **Limpieza Manual**
```bash
# Limpiar logs de más de 90 días (solo backups)
python -c "
from plataforma_cursos.logging_config import cleanup_old_logs
cleaned = cleanup_old_logs(90)
print(f'Archivos eliminados: {cleaned}')
"

# Ver estadísticas antes y después
python -c "
from plataforma_cursos.logging_config import get_log_statistics
import json
stats = get_log_statistics()
print(json.dumps(stats, indent=2, default=str))
"
```

### **Monitoreo en Tiempo Real**
```bash
# Ver logs de seguridad en tiempo real
tail -f logs/security.log

# Ver todos los logs críticos
tail -f logs/critical.log

# Buscar eventos específicos
grep "FAILED_LOGIN" logs/security.log
grep "ERROR" logs/errors.log
```

---

## 📊 **EJEMPLOS DE CONTENIDO DE LOGS**

### **security.log**
```
2024-06-12 14:30:15 [SECURITY] INFO usuarios.decorators: Usuario admin accedió con @superuser_required desde 192.168.1.100
2024-06-12 14:32:22 [SECURITY] WARNING plataforma_cursos.middleware.production_security: Rate limit alcanzado para IP 192.168.1.50 (tipo: login)
2024-06-12 14:35:10 [SECURITY] INFO usuarios.decorators: Login exitoso para usuario: admin
```

### **admin_access.log**
```
2024-06-12 14:30:15 [INFO] plataforma_cursos.middleware.admin_security 1234 5678: Acceso al panel admin desde 192.168.1.100 usuario admin
2024-06-12 14:31:20 [INFO] plataforma_cursos.middleware.admin_security 1234 5678: Creación de objeto Usuario por admin
2024-06-12 14:32:15 [INFO] plataforma_cursos.middleware.admin_security 1234 5678: Sesión admin cerrada por timeout
```

### **errors.log**
```
2024-06-12 14:45:30 [ERROR] django.request 1234 5678: Not Found: /admin/nonexistent/
2024-06-12 14:46:15 [ERROR] cursos.views 1234 5678: Error al procesar inscripción: Invalid course ID
2024-06-12 15:00:00 [ERROR] pagos.views 1234 5678: Webpay API error: Connection timeout
```

---

## ⚙️ **CONFIGURACIÓN AVANZADA**

### **Cambiar Niveles de Logging**
```python
# En settings.py o variables de entorno
LOGGING_LEVEL_SECURITY = 'INFO'    # INFO, WARNING, ERROR
LOGGING_LEVEL_APPLICATION = 'INFO'
LOGGING_LEVEL_ADMIN = 'INFO'
```

### **Configurar Rotación Personalizada**
```python
# En .env
LOG_DIR=logs
SECURITY_LOG_RETENTION_DAYS=30
ADMIN_LOG_RETENTION_WEEKS=4
APPLICATION_LOG_RETENTION_DAYS=7
ERROR_LOG_MAX_SIZE_MB=5
CRITICAL_LOG_MAX_SIZE_MB=10
```

### **Activar/Desactivar Categorías**
```python
# En settings.py
ENABLE_SECURITY_LOGGING = True
ENABLE_ADMIN_LOGGING = True
ENABLE_APPLICATION_LOGGING = True
ENABLE_DETAILED_ERROR_LOGGING = True
```

---

## 🚨 **ALERTAS Y NOTIFICACIONES**

### **Eventos que Generan Alertas**
- 🔴 Logs críticos (`CRITICAL` level)
- 🟠 Rate limiting excedido repetidamente
- 🟡 Errores de autenticación múltiples
- 🔵 Cambios administrativos importantes

### **Configurar Alertas por Email**
```bash
# En .env
ENABLE_SECURITY_EMAIL_ALERTS=True
ADMIN_EMAIL=admin@tudominio.com
SECURITY_ALERT_THRESHOLD=5  # Alertas después de 5 eventos similares
```

---

## 📈 **ANÁLISIS Y REPORTES**

### **Comando de Análisis Rápido**
```bash
python manage.py security_audit --action=log-analysis --days=7
```

### **Generar Reporte Semanal**
```bash
python -c "
from plataforma_cursos.logging_config import LogManager
from datetime import datetime, timedelta

# Analizar últimos 7 días
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

print(f'📊 REPORTE DE LOGS: {start_date.date()} a {end_date.date()}')
print('=' * 50)

# Estadísticas por archivo
from plataforma_cursos.logging_config import get_log_statistics
stats = get_log_statistics()
print(f'Total archivos de log: {stats[\"total_files\"]}')
print(f'Espacio total usado: {stats[\"total_size_mb\"]} MB')
print()

for file_info in stats['files_info']:
    print(f'{file_info[\"name\"]}: {file_info[\"size_mb\"]} MB')
"
```

---

## 🛠️ **MANTENIMIENTO Y MEJORES PRÁCTICAS**

### **Tareas de Mantenimiento Mensual**
1. **Revisar espacio en disco:** `df -h`
2. **Verificar rotación:** Comprobar que se crean archivos de backup
3. **Limpiar logs antiguos:** Ejecutar `cleanup_old_logs()`
4. **Revisar alertas:** Verificar que las alertas funcionan
5. **Actualizar retención:** Ajustar según el crecimiento

### **Optimización para Producción**
```python
# Para sitios de muy bajo tráfico (< 500 usuarios/día)
LOGGING_CONFIG = setup_production_logging(low_traffic=True)

# Para sitios de alto tráfico (> 10000 usuarios/día) 
LOGGING_CONFIG = setup_production_logging(low_traffic=False)
```

### **Backup de Logs Críticos**
```bash
# Crear backup semanal de logs críticos
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/critical.log*
```

---

## 📞 **SOPORTE Y TROUBLESHOOTING**

### **Problemas Comunes**

1. **Logs no se escriben:**
   - Verificar permisos del directorio `logs/`
   - Comprobar configuración en `settings.py`
   - Revisar errores en consola

2. **Archivos de log muy grandes:**
   - Verificar configuración de rotación
   - Reducir nivel de logging
   - Implementar `low_traffic=True`

3. **Espacio en disco lleno:**
   - Ejecutar `cleanup_old_logs()`
   - Reducir `backupCount` en configuración
   - Mover logs antiguos a storage externo

### **Comandos de Diagnóstico**
```bash
# Verificar configuración actual
python manage.py shell -c "
from django.conf import settings
import pprint
pprint.pprint(settings.LOGGING)
"

# Probar logging manualmente
python manage.py shell -c "
import logging
logger = logging.getLogger('usuarios.decorators')
logger.info('Prueba de logging')
logger.warning('Prueba de warning')
logger.error('Prueba de error')
"
```

---

## ✅ **CHECKLIST DE CONFIGURACIÓN**

- [ ] Directorio `logs/` creado con permisos correctos
- [ ] Variables de entorno configuradas
- [ ] Rotación automática funcionando
- [ ] Alertas por email configuradas
- [ ] Espacio en disco monitoreado
- [ ] Backups de logs críticos programados
- [ ] Equipo capacitado en interpretación de logs
- [ ] Procedimientos de respuesta a alertas definidos

---

## 🎮 **DEMOSTRACIÓN PRÁCTICA**

### **Probar el Sistema Completo

```powershell
# 1. Generar eventos de prueba y ver estadísticas
cd "e:\Paulo\Github\plataforma-cursos"
python -c "
import os, django, logging
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plataforma_cursos.settings')
django.setup()

# Generar eventos de seguridad
security_logger = logging.getLogger('usuarios.decorators')
security_logger.info('🔐 Usuario admin verificado')
security_logger.warning('⚠️ Intento de acceso denegado')

# Generar eventos de middleware
middleware_logger = logging.getLogger('plataforma_cursos.middleware.production_security')
middleware_logger.info('🛡️ Rate limiting aplicado')
middleware_logger.warning('🚨 IP sospechosa: 192.168.1.100')

# Generar error de aplicación
django_logger = logging.getLogger('django')
django_logger.error('💥 Error simulado de base de datos')

print('✅ Eventos de prueba generados')
"

# 2. Ver los logs generados
echo "🔍 LOGS DE SEGURIDAD:"
Get-Content logs/security.log -Tail 5

echo "`n🚨 LOGS DE ERRORES:"
Get-Content logs/errors.log -Tail 3

# 3. Estadísticas del sistema
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plataforma_cursos.settings')
django.setup()

from plataforma_cursos.logging_config import get_log_statistics
stats = get_log_statistics()
print(f'📊 Total archivos: {stats[\"total_files\"]}')
print(f'💾 Espacio usado: {stats[\"total_size_mb\"]} MB')
"
```

### **Resultado Esperado**
```
✅ Eventos de prueba generados

🔍 LOGS DE SEGURIDAD:
[11:30:15] INFO usuarios.decorators: 🔐 Usuario admin verificado
[11:30:15] WARNING usuarios.decorators: ⚠️ Intento de acceso denegado
[11:30:15] INFO plataforma_cursos.middleware.production_security: 🛡️ Rate limiting aplicado
[11:30:15] WARNING plataforma_cursos.middleware.production_security: 🚨 IP sospechosa: 192.168.1.100

🚨 LOGS DE ERRORES:
[11:30:15] ERROR django: 💥 Error simulado de base de datos

📊 Total archivos: 2
💾 Espacio usado: 0.001 MB
```

### **Interpretación de Resultados**

1. **✅ Sistema Funcional:** Los logs se escriben correctamente en archivos separados
2. **📱 Categorización:** Eventos de seguridad van a `security.log`, errores a `errors.log`
3. **🔧 Configuración:** En desarrollo usa archivos únicos, en producción rota automáticamente
4. **💾 Eficiencia:** Uso mínimo de espacio, ideal para bajo tráfico

---

## 📝 **RESUMEN EJECUTIVO FINAL**

### **✅ ¿Qué Registra el Sistema?**
- 🔐 **Eventos de seguridad:** Login, permisos, rate limiting
- 🛡️ **Accesos administrativos:** Panel admin, operaciones críticas  
- ⚠️ **Errores de aplicación:** 404, 500, fallos de BD
- 📱 **Eventos importantes:** Suscripciones, pagos, cambios de configuración
- 🚨 **Eventos críticos:** Fallos graves que requieren atención

### **❌ ¿Qué NO Registra?**
- ❌ Navegación normal de usuarios
- ❌ Peticiones HTTP rutinarias
- ❌ Consultas normales a la base de datos
- ❌ Carga de páginas públicas

### **🔄 Gestión de Archivos**
- **Desarrollo:** Archivos únicos sin rotación
- **Producción - Bajo Tráfico:** Rotación diaria/semanal, retención 7-30 días
- **Producción - Alto Tráfico:** Rotación por tamaño, múltiples backups

### **💾 Uso de Espacio Estimado**
- **Bajo tráfico:** 50-100 MB/mes máximo
- **Medio tráfico:** 200-500 MB/mes máximo  
- **Alto tráfico:** 1-2 GB/mes máximo

### **🚀 Beneficios Clave**
1. **Eficiencia:** Solo registra lo importante
2. **Escalabilidad:** Se adapta al tráfico automáticamente
3. **Seguridad:** Auditoría completa de eventos críticos
4. **Mantenimiento:** Limpieza automática de archivos antiguos
5. **Debugging:** Información suficiente para resolver problemas

**🎯 El sistema está optimizado para proporcionar máxima información de seguridad con mínimo impacto en rendimiento y almacenamiento.**
