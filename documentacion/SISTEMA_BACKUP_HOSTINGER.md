# 💾 Sistema de Backup Integral para Django + PostgreSQL en Hostinger VPS

## 📋 **ESTRATEGIA DE BACKUP PARA PRODUCCIÓN**

### **🎯 DATOS A PROTEGER:**

```python
# Datos críticos que debes respaldar:
✅ Base de datos PostgreSQL (usuarios, cursos, transacciones)
✅ Archivos de media (imágenes, documentos subidos)
✅ Archivos estáticos recopilados
✅ Configuraciones (.env, nginx, gunicorn)
✅ Logs de seguridad y transacciones
✅ Certificados SSL
✅ Migraciones de Django aplicadas

# Datos que NO necesitas respaldar:
❌ Archivos de código fuente (están en Git)
❌ Dependencias Python (requirements.txt)
❌ Cache y archivos temporales (__pycache__)
❌ Logs de desarrollo
❌ node_modules (si usas)
```

---

## 🔄 **NIVELES DE BACKUP AUTOMATIZADO**

### **1. Backup Diario Automático (Crítico)**
- **Frecuencia:** Todos los días a las 2:00 AM
- **Retención:** 30 días
- **Contenido:** Base de datos + archivos críticos

### **2. Backup Semanal Completo**
- **Frecuencia:** Domingos a las 1:00 AM
- **Retención:** 12 semanas (3 meses)
- **Contenido:** Todo el sistema

### **3. Backup Mensual Archival**
- **Frecuencia:** Primer día del mes
- **Retención:** 12 meses
- **Contenido:** Snapshot completo comprimido

---

## 🛠️ **SCRIPTS DE BACKUP AUTOMATIZADO**

### **Script Principal de Backup para Django + PostgreSQL**

```bash
#!/bin/bash
# backup_sistema.sh - Backup completo para Django + PostgreSQL en Hostinger

# Variables de configuración
PROJECT_DIR="/home/u123456789/domains/tu-dominio.com/plataforma-cursos"
BACKUP_DIR="/home/u123456789/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función de logging
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Crear directorio de backup
mkdir -p $BACKUP_DIR/{daily,weekly,monthly}

log "🚀 Iniciando backup del sistema Django..."

# 1. BACKUP DE BASE DE DATOS POSTGRESQL
log "📊 Respaldando base de datos PostgreSQL..."

# Cargar variables de entorno
source $PROJECT_DIR/.env

# Backup de PostgreSQL con pg_dump
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME \
    --no-password \
    --verbose \
    --format=custom \
    --compress=9 \
    --file=$BACKUP_DIR/daily/db_backup_$DATE.dump

if [ $? -eq 0 ]; then
    log "✅ Backup de PostgreSQL completado"
    
    # Crear también backup en formato SQL para facilidad de lectura
    pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME \
        --no-password \
        --format=plain \
        --file=$BACKUP_DIR/daily/db_backup_$DATE.sql
    
    # Comprimir el archivo SQL
    gzip $BACKUP_DIR/daily/db_backup_$DATE.sql
    log "✅ Backup SQL comprimido creado"
else
    error "❌ Error en backup de PostgreSQL"
    exit 1
fi

# 2. BACKUP DE ARCHIVOS DE MEDIA
log "📁 Respaldando archivos de media..."

if [ -d "$PROJECT_DIR/media" ]; then
    tar -czf $BACKUP_DIR/daily/media_backup_$DATE.tar.gz \
        -C $PROJECT_DIR media/
    log "✅ Backup de media completado"
else
    warning "⚠️ Directorio media no encontrado"
fi

# 3. BACKUP DE ARCHIVOS ESTÁTICOS
log "🎨 Respaldando archivos estáticos..."

if [ -d "$PROJECT_DIR/staticfiles" ]; then
    tar -czf $BACKUP_DIR/daily/static_backup_$DATE.tar.gz \
        -C $PROJECT_DIR staticfiles/
    log "✅ Backup de estáticos completado"
else
    warning "⚠️ Directorio staticfiles no encontrado"
fi

# 4. BACKUP DE CONFIGURACIONES
log "⚙️ Respaldando configuraciones..."

# Crear directorio temporal para configuraciones
mkdir -p /tmp/config_backup_$DATE

# Copiar archivos de configuración
cp $PROJECT_DIR/.env /tmp/config_backup_$DATE/
cp /etc/nginx/sites-available/tu-dominio.com /tmp/config_backup_$DATE/nginx_config
cp /etc/systemd/system/plataforma-cursos.service /tmp/config_backup_$DATE/gunicorn_service

# Backup de migraciones aplicadas de Django
cd $PROJECT_DIR
python manage.py showmigrations --format=json > /tmp/config_backup_$DATE/django_migrations.json

# Comprimir configuraciones
tar -czf $BACKUP_DIR/daily/config_backup_$DATE.tar.gz \
    -C /tmp config_backup_$DATE/

# Limpiar temporal
rm -rf /tmp/config_backup_$DATE

log "✅ Backup de configuraciones completado"

# 5. BACKUP DE LOGS CRÍTICOS
log "📝 Respaldando logs críticos..."

if [ -d "$PROJECT_DIR/logs" ]; then
    tar -czf $BACKUP_DIR/daily/logs_backup_$DATE.tar.gz \
        -C $PROJECT_DIR logs/
    log "✅ Backup de logs completado"
fi

# 6. CREAR MANIFIESTO DEL BACKUP
log "📋 Creando manifiesto del backup..."

cat > $BACKUP_DIR/daily/manifest_$DATE.txt << EOF
BACKUP MANIFEST - Django + PostgreSQL
=====================================
Fecha: $(date)
Servidor: $(hostname)
Usuario: $(whoami)

CONTENIDO DEL BACKUP:
- Base de datos: db_backup_$DATE.dump (PostgreSQL custom format)
- Base de datos SQL: db_backup_$DATE.sql.gz (SQL comprimido)
- Archivos media: media_backup_$DATE.tar.gz
- Archivos estáticos: static_backup_$DATE.tar.gz
- Configuraciones: config_backup_$DATE.tar.gz
- Logs: logs_backup_$DATE.tar.gz

ESTADÍSTICAS:
- Tamaño BD: $(du -h $BACKUP_DIR/daily/db_backup_$DATE.dump 2>/dev/null | cut -f1 || echo "N/A")
- Total archivos: $(find $BACKUP_DIR/daily/*_$DATE.* -type f | wc -l)
- Espacio usado: $(du -sh $BACKUP_DIR/daily/ | cut -f1)

VERIFICACIÓN:
- Integridad PostgreSQL: $(pg_restore --list $BACKUP_DIR/daily/db_backup_$DATE.dump >/dev/null 2>&1 && echo "OK" || echo "ERROR")
EOF

log "✅ Manifiesto creado"

# 7. LIMPIEZA DE BACKUPS ANTIGUOS
log "🧹 Limpiando backups antiguos (>${RETENTION_DAYS} días)..."

find $BACKUP_DIR/daily -name "*_[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_*" -mtime +$RETENTION_DAYS -delete
log "✅ Limpieza completada"

# 8. VERIFICACIÓN DE INTEGRIDAD
log "🔍 Verificando integridad de backups..."

# Verificar que el dump de PostgreSQL esté íntegro
if pg_restore --list $BACKUP_DIR/daily/db_backup_$DATE.dump >/dev/null 2>&1; then
    log "✅ Backup de PostgreSQL verificado correctamente"
else
    error "❌ Backup de PostgreSQL corrupto!"
    exit 1
fi

# Verificar archivos tar
for file in $BACKUP_DIR/daily/*_$DATE.tar.gz; do
    if [ -f "$file" ]; then
        if tar -tzf "$file" >/dev/null 2>&1; then
            log "✅ $(basename $file) verificado"
        else
            error "❌ $(basename $file) corrupto!"
        fi
    fi
done

# 9. ESTADÍSTICAS FINALES
BACKUP_SIZE=$(du -sh $BACKUP_DIR/daily/ | cut -f1)
log "📊 Backup completado exitosamente"
log "💾 Espacio total usado: $BACKUP_SIZE"
log "📅 Próximo backup: $(date -d '+1 day')"

# 10. NOTIFICACIÓN (OPCIONAL)
if [ "$ENABLE_EMAIL_NOTIFICATIONS" = "True" ]; then
    # Enviar email de confirmación
    echo "Backup completado exitosamente el $(date). Tamaño: $BACKUP_SIZE" | \
    mail -s "✅ Backup exitoso - $(hostname)" $ADMIN_EMAIL
fi

log "🎉 Backup completado!"
```

---

## 📅 **SCRIPTS DE BACKUP POR FRECUENCIA**

### **Backup Semanal (Domingos)**

```bash
#!/bin/bash
# backup_semanal.sh - Backup semanal completo

source /home/u123456789/domains/tu-dominio.com/plataforma-cursos/backup_sistema.sh

# Copiar backup diario a semanal
DATE=$(date +%Y%m%d_%H%M%S)
WEEK=$(date +%Y_semana_%V)

mkdir -p $BACKUP_DIR/weekly/$WEEK

# Copiar archivos del backup diario más reciente
LATEST_DAILY=$(ls -t $BACKUP_DIR/daily/db_backup_*.dump | head -1)
LATEST_DATE=$(basename $LATEST_DAILY | sed 's/db_backup_\(.*\)\.dump/\1/')

cp $BACKUP_DIR/daily/*_$LATEST_DATE.* $BACKUP_DIR/weekly/$WEEK/

# Crear backup adicional con información del sistema
cat > $BACKUP_DIR/weekly/$WEEK/system_info_$DATE.txt << EOF
INFORMACIÓN DEL SISTEMA - BACKUP SEMANAL
=======================================
Fecha: $(date)
Uptime: $(uptime)
Memoria: $(free -h)
Disco: $(df -h)
Procesos Django: $(ps aux | grep python | grep manage.py | wc -l)
Estado PostgreSQL: $(systemctl is-active postgresql)
Estado Nginx: $(systemctl is-active nginx)
Estado Gunicorn: $(systemctl is-active plataforma-cursos)

VERSIONES:
Python: $(python3 --version)
Django: $(cd /home/u123456789/domains/tu-dominio.com/plataforma-cursos && python manage.py --version)
PostgreSQL: $(psql --version)

PAQUETES INSTALADOS:
$(cd /home/u123456789/domains/tu-dominio.com/plataforma-cursos && pip list)
EOF

echo "✅ Backup semanal completado en: $BACKUP_DIR/weekly/$WEEK"
```

### **Backup Mensual (Primer día del mes)**

```bash
#!/bin/bash
# backup_mensual.sh - Backup mensual para archivo

DATE=$(date +%Y%m%d_%H%M%S)
MONTH=$(date +%Y_%m)
PROJECT_DIR="/home/u123456789/domains/tu-dominio.com/plataforma-cursos"
BACKUP_DIR="/home/u123456789/backups"

mkdir -p $BACKUP_DIR/monthly/$MONTH

echo "🗄️ Creando backup mensual para $MONTH..."

# 1. Backup completo de la base de datos con todas las opciones
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME \
    --no-password \
    --verbose \
    --format=custom \
    --compress=9 \
    --blobs \
    --create \
    --clean \
    --if-exists \
    --file=$BACKUP_DIR/monthly/$MONTH/db_complete_$DATE.dump

# 2. Crear snapshot completo del proyecto (excepto .git)
tar --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='node_modules' \
    --exclude='venv' \
    -czf $BACKUP_DIR/monthly/$MONTH/project_snapshot_$DATE.tar.gz \
    -C $(dirname $PROJECT_DIR) $(basename $PROJECT_DIR)

# 3. Backup de configuraciones del sistema
mkdir -p /tmp/system_config_$DATE
cp -r /etc/nginx /tmp/system_config_$DATE/
cp -r /etc/systemd/system/plataforma-cursos.service /tmp/system_config_$DATE/
crontab -l > /tmp/system_config_$DATE/crontab_backup.txt 2>/dev/null || echo "Sin crontab"

tar -czf $BACKUP_DIR/monthly/$MONTH/system_config_$DATE.tar.gz \
    -C /tmp system_config_$DATE/

rm -rf /tmp/system_config_$DATE

# 4. Crear checksum para verificación de integridad
cd $BACKUP_DIR/monthly/$MONTH
sha256sum * > checksums_$DATE.txt

echo "✅ Backup mensual completado para $MONTH"
```

---

## ⚙️ **CONFIGURACIÓN DE CRONTAB**

```bash
# Agregar a crontab con: crontab -e

# Backup diario a las 2:00 AM
0 2 * * * /home/u123456789/scripts/backup_sistema.sh >> /home/u123456789/logs/backup.log 2>&1

# Backup semanal domingos a la 1:00 AM
0 1 * * 0 /home/u123456789/scripts/backup_semanal.sh >> /home/u123456789/logs/backup_semanal.log 2>&1

# Backup mensual el día 1 a las 00:30 AM
30 0 1 * * /home/u123456789/scripts/backup_mensual.sh >> /home/u123456789/logs/backup_mensual.log 2>&1

# Verificación de espacio en disco diaria
0 6 * * * df -h | grep -E "/(|home|var)" | awk '$5+0 > 85 {print "⚠️ Disco casi lleno: " $0}' | mail -s "⚠️ Alerta de disco" $ADMIN_EMAIL

# Limpieza de logs antiguos
0 3 * * 0 find /home/u123456789/logs -name "*.log" -mtime +30 -delete
```

---

## 🔧 **COMANDOS DE GESTIÓN DE BACKUP**

### **Verificar Estado de Backups**

```bash
#!/bin/bash
# check_backups.sh - Verificar estado de backups

BACKUP_DIR="/home/u123456789/backups"

echo "📊 ESTADO DE BACKUPS - $(date)"
echo "================================"

# Backups diarios
echo "📅 BACKUPS DIARIOS:"
if [ -d "$BACKUP_DIR/daily" ]; then
    echo "  Total archivos: $(find $BACKUP_DIR/daily -name "db_backup_*.dump" | wc -l)"
    echo "  Último backup: $(ls -t $BACKUP_DIR/daily/db_backup_*.dump | head -1 | xargs basename)"
    echo "  Espacio usado: $(du -sh $BACKUP_DIR/daily | cut -f1)"
else
    echo "  ❌ No hay backups diarios"
fi

# Backups semanales
echo ""
echo "📅 BACKUPS SEMANALES:"
if [ -d "$BACKUP_DIR/weekly" ]; then
    echo "  Semanas respaldadas: $(ls $BACKUP_DIR/weekly | wc -l)"
    echo "  Espacio usado: $(du -sh $BACKUP_DIR/weekly | cut -f1)"
else
    echo "  ❌ No hay backups semanales"
fi

# Backups mensuales
echo ""
echo "📅 BACKUPS MENSUALES:"
if [ -d "$BACKUP_DIR/monthly" ]; then
    echo "  Meses respaldados: $(ls $BACKUP_DIR/monthly | wc -l)"
    echo "  Espacio usado: $(du -sh $BACKUP_DIR/monthly | cut -f1)"
else
    echo "  ❌ No hay backups mensuales"
fi

# Espacio total
echo ""
echo "💾 ESPACIO TOTAL DE BACKUPS: $(du -sh $BACKUP_DIR | cut -f1)"

# Verificar último backup
LAST_BACKUP=$(ls -t $BACKUP_DIR/daily/db_backup_*.dump 2>/dev/null | head -1)
if [ -n "$LAST_BACKUP" ]; then
    BACKUP_AGE=$(stat -c %Y "$LAST_BACKUP")
    CURRENT_TIME=$(date +%s)
    AGE_HOURS=$(( (CURRENT_TIME - BACKUP_AGE) / 3600 ))
    
    echo ""
    if [ $AGE_HOURS -lt 25 ]; then
        echo "✅ Último backup: hace $AGE_HOURS horas (OK)"
    else
        echo "⚠️ Último backup: hace $AGE_HOURS horas (ALERTA: muy antiguo)"
    fi
fi
```

---

## 🚨 **RESTAURACIÓN DE BACKUP**

### **Script de Restauración PostgreSQL**

```bash
#!/bin/bash
# restore_backup.sh - Restaurar backup de PostgreSQL

if [ "$#" -ne 1 ]; then
    echo "Uso: $0 <archivo_backup.dump>"
    echo "Ejemplo: $0 /home/u123456789/backups/daily/db_backup_20250612_020001.dump"
    exit 1
fi

BACKUP_FILE=$1
PROJECT_DIR="/home/u123456789/domains/tu-dominio.com/plataforma-cursos"

# Verificar que el archivo existe
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Error: Archivo de backup no encontrado: $BACKUP_FILE"
    exit 1
fi

# Cargar variables de entorno
source $PROJECT_DIR/.env

echo "⚠️ ADVERTENCIA: Esto sobrescribirá la base de datos actual!"
echo "Base de datos: $DB_NAME"
echo "Archivo backup: $BACKUP_FILE"
echo ""
read -p "¿Estás seguro? (escribe 'SI' para continuar): " confirmacion

if [ "$confirmacion" != "SI" ]; then
    echo "❌ Restauración cancelada"
    exit 1
fi

echo "🚀 Iniciando restauración..."

# 1. Detener la aplicación Django
echo "🛑 Deteniendo aplicación Django..."
sudo systemctl stop plataforma-cursos

# 2. Crear backup de seguridad de la BD actual
echo "💾 Creando backup de seguridad de la BD actual..."
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME \
    --no-password \
    --format=custom \
    --file=/tmp/backup_before_restore_$(date +%Y%m%d_%H%M%S).dump

# 3. Restaurar la base de datos
echo "📥 Restaurando base de datos..."
pg_restore -h $DB_HOST -U $DB_USER -d $DB_NAME \
    --no-password \
    --verbose \
    --clean \
    --if-exists \
    --create \
    "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Restauración de BD completada"
else
    echo "❌ Error en la restauración"
    exit 1
fi

# 4. Ejecutar migraciones por si acaso
echo "🔄 Ejecutando migraciones Django..."
cd $PROJECT_DIR
python manage.py migrate --fake-initial

# 5. Recopilar archivos estáticos
echo "🎨 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# 6. Reiniciar aplicación
echo "🚀 Reiniciando aplicación Django..."
sudo systemctl start plataforma-cursos

# 7. Verificar estado
echo "🔍 Verificando estado..."
sleep 5
if systemctl is-active --quiet plataforma-cursos; then
    echo "✅ Aplicación restaurada y funcionando"
else
    echo "❌ Error: La aplicación no está funcionando"
    echo "Revisa los logs: journalctl -u plataforma-cursos -f"
fi

echo "🎉 Restauración completada!"
```

---

## 📧 **NOTIFICACIONES Y MONITOREO**

### **Script de Monitoreo de Backup**

```bash
#!/bin/bash
# monitor_backups.sh - Monitoreo y alertas de backup

BACKUP_DIR="/home/u123456789/backups"
ADMIN_EMAIL="admin@tu-dominio.com"

# Verificar si hay backup reciente (últimas 25 horas)
LAST_BACKUP=$(ls -t $BACKUP_DIR/daily/db_backup_*.dump 2>/dev/null | head -1)

if [ -z "$LAST_BACKUP" ]; then
    echo "🚨 ERROR: No se encontraron backups" | \
    mail -s "🚨 ALERTA: Sin backups - $(hostname)" $ADMIN_EMAIL
    exit 1
fi

BACKUP_AGE=$(stat -c %Y "$LAST_BACKUP")
CURRENT_TIME=$(date +%s)
AGE_HOURS=$(( (CURRENT_TIME - BACKUP_AGE) / 3600 ))

if [ $AGE_HOURS -gt 25 ]; then
    echo "🚨 ALERTA: Último backup hace $AGE_HOURS horas" | \
    mail -s "🚨 ALERTA: Backup antiguo - $(hostname)" $ADMIN_EMAIL
fi

# Verificar espacio en disco
DISK_USAGE=$(df -h $BACKUP_DIR | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 85 ]; then
    echo "🚨 ALERTA: Espacio de backup al $DISK_USAGE%" | \
    mail -s "🚨 ALERTA: Espacio de backup - $(hostname)" $ADMIN_EMAIL
fi

# Verificar integridad del último backup
if ! pg_restore --list "$LAST_BACKUP" >/dev/null 2>&1; then
    echo "🚨 ERROR: Último backup corrupto: $LAST_BACKUP" | \
    mail -s "🚨 ALERTA: Backup corrupto - $(hostname)" $ADMIN_EMAIL
fi

echo "✅ Monitoreo de backup completado - $(date)"
```

---

## 💡 **MEJORES PRÁCTICAS DE BACKUP**

### **1. Configuración de PostgreSQL para Backup**

```bash
# En /etc/postgresql/*/main/postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /home/u123456789/wal_archive/%f'
max_wal_senders = 3
```

### **2. Variables de Entorno para Backup**

```bash
# Agregar a .env
BACKUP_RETENTION_DAYS=30
BACKUP_ENCRYPTION_KEY=tu_clave_secreta_backup
ENABLE_EMAIL_NOTIFICATIONS=True
ADMIN_EMAIL=admin@tu-dominio.com
PGPASSWORD=tu_password_postgresql
```

### **3. Seguridad de Backups**

```bash
# Encriptar backups sensibles
gpg --symmetric --cipher-algo AES256 --compress-algo 1 \
    --s2k-mode 3 --s2k-digest-algo SHA512 --s2k-count 65536 \
    --output backup_encrypted.gpg backup_file.dump

# Desencriptar
gpg --decrypt backup_encrypted.gpg > backup_restored.dump
```

---

## 📋 **CHECKLIST DE IMPLEMENTACIÓN**

### **Configuración Inicial:**
- [ ] Crear directorios de backup
- [ ] Configurar PostgreSQL para backup
- [ ] Crear scripts de backup
- [ ] Configurar crontab
- [ ] Probar restauración
- [ ] Configurar monitoreo
- [ ] Configurar notificaciones

### **Mantenimiento Mensual:**
- [ ] Verificar integridad de backups
- [ ] Probar proceso de restauración
- [ ] Revisar espacio en disco
- [ ] Actualizar scripts si es necesario
- [ ] Documentar cambios importantes

---

## 🎯 **ESTRATEGIA ESPECÍFICA PARA TU PROYECTO**

### **Datos Sensibles que Manejas:**
```python
# DATOS CRÍTICOS A PROTEGER:
✅ Usuarios y contraseñas (hasheadas)
✅ Emails y preferencias
✅ Registros de transacciones
✅ Historiales de acceso
✅ Contenido de cursos
✅ Logs de seguridad
✅ Configuraciones de pago

# FRECUENCIA RECOMENDADA:
⏰ Diario: Base de datos + media
⏰ Semanal: Snapshot completo
⏰ Mensual: Archivo a largo plazo
⏰ Antes de updates: Backup manual
```

### **Comando de Backup Manual Rápido:**

```bash
# Para antes de hacer cambios importantes
sudo -u postgres pg_dump plataforma_cursos > backup_pre_cambios_$(date +%Y%m%d).sql
tar -czf media_pre_cambios_$(date +%Y%m%d).tar.gz media/
cp .env .env.backup.$(date +%Y%m%d)
```

**🎯 Con este sistema tendrás backups automáticos, seguros y restaurables para proteger todos los datos de tu plataforma de cursos.**
