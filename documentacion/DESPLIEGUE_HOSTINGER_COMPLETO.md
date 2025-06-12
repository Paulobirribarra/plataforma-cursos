# 🚀 Guía de Despliegue en Hostinger VPS

## 📋 **RESUMEN DE HOSTINGER PARA DJANGO**

### **✅ POR QUÉ HOSTINGER ES BUENA OPCIÓN:**

```bash
✅ VPS con acceso SSH completo
✅ Python 3.x preinstalado
✅ MySQL/PostgreSQL incluido
✅ SSL gratuito con Let's Encrypt
✅ Panel de control hPanel intuitivo
✅ Backups automáticos incluidos
✅ Soporte 24/7 en español
✅ Precio competitivo
✅ Recursos escalables
✅ Ubicación de servidores global
```

### **🎯 CONFIGURACIÓN RECOMENDADA:**
- **VPS Plan:** Cloud Startup (mínimo) o Cloud Professional (recomendado)
- **Recursos:** 2 CPU, 4GB RAM, 80GB SSD
- **SO:** Ubuntu 20.04/22.04 LTS
- **Ubicación:** Según tu audiencia (Europa/América)

---

## 🔧 **PASO A PASO PARA DESPLIEGUE**

### **1. Configuración Inicial del VPS**

```bash
# Conectar por SSH (Hostinger te da estos datos)
ssh u123456789@tu-ip-del-vps

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias básicas
sudo apt install -y python3-pip python3-venv python3-dev
sudo apt install -y mysql-server mysql-client libmysqlclient-dev
sudo apt install -y nginx git curl wget htop
sudo apt install -y certbot python3-certbot-nginx
```

### **2. Configurar Python y Entorno Virtual**

```bash
# Ir al directorio del dominio
cd /home/u123456789/domains/tu-dominio.com/

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar Django y dependencias
pip install django python-decouple mysqlclient
pip install gunicorn whitenoise django-allauth
```

### **3. Clonar y Configurar tu Proyecto**

```bash
# Clonar tu repositorio
git clone https://github.com/tu-usuario/plataforma-cursos.git
cd plataforma-cursos

# Instalar dependencias
pip install -r requirements.txt

# Copiar configuración de Hostinger
cp .env.hostinger.example .env

# Editar variables de entorno
nano .env
```

### **4. Configurar Base de Datos MySQL**

```bash
# Conectar a MySQL
sudo mysql -u root -p

# Crear base de datos y usuario
CREATE DATABASE u123456789_plataforma CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'u123456789_django'@'localhost' IDENTIFIED BY 'password_seguro';
GRANT ALL PRIVILEGES ON u123456789_plataforma.* TO 'u123456789_django'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### **5. Configurar Django**

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recopilar archivos estáticos
python manage.py collectstatic --noinput

# Probar funcionamiento
python manage.py runserver 0.0.0.0:8000
```

### **6. Configurar Nginx**

```bash
# Crear configuración de Nginx
sudo nano /etc/nginx/sites-available/tu-dominio.com
```

```nginx
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;
    
    # Redirigir HTTP a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu-dominio.com www.tu-dominio.com;
    
    # Configuración SSL (Let's Encrypt automáticamente configurará esto)
    
    # Archivos estáticos
    location /static/ {
        alias /home/u123456789/domains/tu-dominio.com/plataforma-cursos/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /home/u123456789/domains/tu-dominio.com/plataforma-cursos/media/;
        expires 30d;
    }
    
    # Proxear a Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Rate limiting básico
        limit_req zone=general burst=10 nodelay;
    }
    
    # Headers de seguridad
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}

# Rate limiting zones
http {
    limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
}
```

```bash
# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/tu-dominio.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### **7. Configurar SSL con Let's Encrypt**

```bash
# Obtener certificado SSL gratuito
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Verificar renovación automática
sudo systemctl status certbot.timer
```

### **8. Configurar Gunicorn como Servicio**

```bash
# Crear archivo de servicio
sudo nano /etc/systemd/system/plataforma-cursos.service
```

```ini
[Unit]
Description=Plataforma de Cursos Django App
After=network.target

[Service]
User=u123456789
Group=u123456789
WorkingDirectory=/home/u123456789/domains/tu-dominio.com/plataforma-cursos
Environment="PATH=/home/u123456789/domains/tu-dominio.com/venv/bin"
ExecStart=/home/u123456789/domains/tu-dominio.com/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    plataforma_cursos.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar y iniciar servicio
sudo systemctl daemon-reload
sudo systemctl enable plataforma-cursos
sudo systemctl start plataforma-cursos
sudo systemctl status plataforma-cursos
```

---

## 🛡️ **CONFIGURACIÓN DE SEGURIDAD ESPECÍFICA**

### **1. Configurar Firewall (UFW)**

```bash
# Habilitar UFW
sudo ufw enable

# Reglas básicas
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Permitir servicios esenciales
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw allow mysql

# Ver estado
sudo ufw status verbose
```

### **2. Configurar Fail2Ban**

```bash
# Instalar Fail2Ban
sudo apt install fail2ban

# Crear configuración personalizada
sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 1800
findtime = 300
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = %(sshd_log)s
backend = %(sshd_backend)s

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-noscript]
enabled = true
port = http,https
filter = nginx-noscript
logpath = /var/log/nginx/access.log
maxretry = 6

[nginx-badbots]
enabled = true
port = http,https
filter = nginx-badbots
logpath = /var/log/nginx/access.log
maxretry = 2
```

```bash
# Reiniciar Fail2Ban
sudo systemctl restart fail2ban
sudo fail2ban-client status
```

### **3. Configurar tu Sistema de Seguridad Django**

```bash
# Activar entorno virtual
source venv/bin/activate

# Configurar settings.py para Hostinger
nano plataforma_cursos/settings.py
```

```python
# Agregar al final de settings.py
from plataforma_cursos.hostinger_security import apply_hostinger_settings

# Aplicar configuraciones específicas de Hostinger
apply_hostinger_settings(locals())

# Middleware específico para Hostinger
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    
    # Middleware de seguridad integral para Hostinger VPS
    "plataforma_cursos.middleware.admin_security.AdminSecurityMiddleware",
    "plataforma_cursos.middleware.hostinger_security.HostingerVPSSecurityMiddleware",
    "plataforma_cursos.middleware.hostinger_security.HostingerRateLimitMiddleware",
    "plataforma_cursos.middleware.hostinger_security.HostingerFirewallMiddleware",
]

# Configuración específica para VPS
USE_IPTABLES_BLOCKING = True
ENABLE_FAIL2BAN = True
```

### **4. Ejecutar Auditoría de Seguridad**

```bash
# Verificar configuración de seguridad
python manage.py security_audit --action=check-config

# Auditoría completa
python manage.py security_audit

# Crear usuario admin seguro
python manage.py security_audit --action=create-admin
```

---

## 📊 **MONITOREO Y MANTENIMIENTO**

### **1. Scripts de Monitoreo**

```bash
# Crear script de monitoreo
nano ~/monitor_plataforma.sh
```

```bash
#!/bin/bash
# Monitor para plataforma de cursos en Hostinger

echo "=== MONITOREO PLATAFORMA CURSOS $(date) ==="

# Estado del servicio Django
echo "📱 Estado Django:"
sudo systemctl status plataforma-cursos --no-pager -l

# Estado de Nginx
echo "🌐 Estado Nginx:"
sudo systemctl status nginx --no-pager

# Estado de MySQL
echo "🗄️ Estado MySQL:"
sudo systemctl status mysql --no-pager

# Uso de disco
echo "💾 Uso de disco:"
df -h

# Uso de memoria
echo "🧠 Uso de memoria:"
free -h

# Procesos de Python
echo "🐍 Procesos Python:"
ps aux | grep python

# Últimos logs de error
echo "🚨 Últimos errores:"
tail -5 /var/log/nginx/error.log

# Logs de seguridad Django
echo "🔒 Logs de seguridad:"
tail -5 ~/domains/tu-dominio.com/plataforma-cursos/logs/security.log
```

```bash
# Hacer ejecutable
chmod +x ~/monitor_plataforma.sh

# Agregar a crontab para ejecutar cada hora
crontab -e
# Agregar línea: 0 * * * * /home/u123456789/monitor_plataforma.sh >> /home/u123456789/monitor.log
```

### **2. Backup Automatizado**

```bash
# Crear script de backup
nano ~/backup_plataforma.sh
```

```bash
#!/bin/bash
# Backup automatizado para Hostinger

BACKUP_DIR="/home/u123456789/backups"
DATE=$(date +%Y%m%d_%H%M%S)
PROJECT_DIR="/home/u123456789/domains/tu-dominio.com/plataforma-cursos"

# Crear directorio de backup
mkdir -p $BACKUP_DIR

# Backup de base de datos
mysqldump -u u123456789_django -p'password_seguro' u123456789_plataforma > $BACKUP_DIR/db_backup_$DATE.sql

# Backup de archivos de media
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz $PROJECT_DIR/media/

# Backup de configuración
cp $PROJECT_DIR/.env $BACKUP_DIR/env_backup_$DATE

# Limpiar backups antiguos (más de 30 días)
find $BACKUP_DIR -type f -mtime +30 -delete

echo "✅ Backup completado: $DATE"
```

```bash
# Hacer ejecutable y programar
chmod +x ~/backup_plataforma.sh

# Agregar a crontab para backup diario a las 2 AM
crontab -e
# Agregar línea: 0 2 * * * /home/u123456789/backup_plataforma.sh
```

---

## 🚨 **SOLUCIÓN DE PROBLEMAS COMUNES**

### **1. Error de Conexión a Base de Datos**
```bash
# Verificar estado de MySQL
sudo systemctl status mysql

# Verificar conexión
mysql -u u123456789_django -p u123456789_plataforma

# Verificar configuración en .env
grep DB_ .env
```

### **2. Error 500 en Django**
```bash
# Ver logs de Django
tail -f logs/errors.log

# Ver logs de Nginx
sudo tail -f /var/log/nginx/error.log

# Verificar permisos
ls -la staticfiles/
ls -la media/
```

### **3. Problemas de SSL**
```bash
# Verificar certificados
sudo certbot certificates

# Renovar manualmente
sudo certbot renew --dry-run

# Verificar configuración Nginx
sudo nginx -t
```

### **4. Alto Uso de Recursos**
```bash
# Ver procesos que más consumen
htop

# Ver logs de acceso sospechoso
sudo tail -f /var/log/nginx/access.log | grep -E "(404|500)"

# Ejecutar auditoría de seguridad
python manage.py security_audit --action=check-threats
```

---

## ✅ **CHECKLIST FINAL DE DESPLIEGUE**

### **Configuración Básica**
- [ ] VPS configurado con Ubuntu
- [ ] Python 3.x y dependencias instaladas
- [ ] MySQL configurado y funcionando
- [ ] Proyecto clonado y dependencias instaladas
- [ ] Variables de entorno configuradas

### **Servicios Web**
- [ ] Nginx instalado y configurado
- [ ] Gunicorn funcionando como servicio
- [ ] SSL configurado con Let's Encrypt
- [ ] Archivos estáticos servidos correctamente

### **Seguridad**
- [ ] Firewall UFW configurado
- [ ] Fail2Ban instalado y funcionando
- [ ] Middleware de seguridad activado
- [ ] URL de admin cambiada
- [ ] Auditoría de seguridad ejecutada

### **Monitoreo**
- [ ] Scripts de monitoreo configurados
- [ ] Backup automatizado funcionando
- [ ] Logs de seguridad activos
- [ ] Alertas por email configuradas

### **Testing Final**
- [ ] Sitio accesible por HTTPS
- [ ] Panel de admin funcionando
- [ ] Formularios funcionando
- [ ] Pagos (Webpay) funcionando
- [ ] Email SMTP funcionando

---

## 📞 **RECURSOS DE SOPORTE HOSTINGER**

### **Contacto Hostinger**
- 🌐 Panel: https://hpanel.hostinger.com
- 📧 Soporte: soporte@hostinger.com
- 💬 Chat: Disponible 24/7 en hPanel
- 📚 Documentación: https://support.hostinger.com

### **Información de tu VPS**
- 🔑 SSH: `ssh u123456789@tu-ip-del-vps`
- 📁 Archivos: `/home/u123456789/domains/tu-dominio.com/`
- 🗄️ Logs: `/var/log/nginx/` y `~/domains/tu-dominio.com/plataforma-cursos/logs/`
- ⚙️ Config: `/etc/nginx/sites-available/tu-dominio.com`

### **Comandos de Emergencia**
```bash
# Reiniciar servicios
sudo systemctl restart nginx
sudo systemctl restart plataforma-cursos
sudo systemctl restart mysql

# Ver logs en tiempo real
sudo tail -f /var/log/nginx/error.log
tail -f ~/domains/tu-dominio.com/plataforma-cursos/logs/security.log

# Verificar seguridad
python manage.py security_audit --action=emergency-check
```

**🎯 Con esta configuración tendrás una plataforma de cursos completamente segura y optimizada en Hostinger VPS.**

---

## 🚀 **SIGUIENTE PASO**

Una vez configurado todo, ejecuta:

```bash
# Verificación final completa
python manage.py security_audit --action=production-ready-check
```

¡Tu plataforma estará lista para recibir estudiantes de forma segura! 🎓
