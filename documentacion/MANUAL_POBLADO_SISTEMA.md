# 📋 Manual de Poblado Completo del Sistema
## Plataforma de Cursos - Guía Paso a Paso

---

## 🎯 Objetivo
Este manual te guiará paso a paso para configurar y poblar completamente el sistema de la plataforma de cursos desde cero.

---

## 📦 Pre-requisitos

### 1. Verificar instalación del entorno
```bash
# Verificar que el entorno virtual esté activado
# Debe aparecer (.venv) al inicio de la línea de comandos
```

### 2. Verificar dependencias
```bash
# Verificar que todas las dependencias estén instaladas
pip install -r requirements.txt
```

---

## 🗄️ PASO 1: Migración Completa de la Base de Datos

### Opción A: Script Automático (Recomendado)
```bash
# Windows PowerShell
.\migration_master.ps1

# Windows CMD
migration_master.bat

# Linux/Mac
./migration_master.sh
```

**Ubicación del archivo:** `migration_master.ps1` / `migration_master.bat` / `migration_master.sh`

### Opción B: Manual (si los scripts no funcionan)
```bash
# 1. Limpiar migraciones existentes (CUIDADO: solo en desarrollo)
python manage.py migrate --fake-initial

# 2. Crear nuevas migraciones
python manage.py makemigrations usuarios
python manage.py makemigrations membresias  
python manage.py makemigrations cursos
python manage.py makemigrations boletines
python manage.py makemigrations blogs
python manage.py makemigrations carrito
python manage.py makemigrations pagos

# 3. Aplicar migraciones
python manage.py migrate
```

---

## 👤 PASO 2: Crear Super Usuario

```bash
# Crear el usuario administrador del sistema
python manage.py createsuperuser
```

**Datos recomendados:**
- Email: `admin@plataforma.com`
- Contraseña: `Admin12345!`

**📁 Ubicación:** Comando de Django integrado

---

## 🚀 PASO 3: Poblado Completo del Sistema

### Opción A: Poblado Automático Completo (Recomendado)
```bash
# Ejecutar script maestro que puebla todo el sistema
python manage.py populate_master --action complete
```

**📁 Ubicación:** `usuarios/management/commands/populate_master.py`

### Opción B: Poblado Manual por Componentes

#### 3.1 Poblar Planes de Membresía
```bash
python manage.py populate_membresias --verbose
```
**📁 Ubicación:** `membresias/management/commands/populate_membresias.py`

**Crea:**
- Plan Básico ($15.000/mes)
- Plan Intermedio ($25.000/mes) 
- Plan Premium ($40.000/mes)

#### 3.2 Poblar Cursos del Sistema
```bash
python manage.py populate_cursos --verbose
```
**📁 Ubicación:** `cursos/management/commands/populate_cursos.py`

**Crea:**
- 6 categorías de cursos
- 41 cursos distribuidos en las categorías
- Asigna instructores automáticamente

#### 3.3 Poblar Tipos de Consulta
```bash
python manage.py populate_tipos_consulta --verbose
```
**📁 Ubicación:** `membresias/management/commands/populate_tipos_consulta.py`

**Crea:**
- Asesoría Grupal (todos los planes)
- Consulta Individual (solo premium)
- Revisión de Portafolio (solo premium)
- Sesión de Trading (intermedio y premium)
- Webinar Exclusivo (solo premium)

#### 3.4 Poblar Cursos Gratuitos
```bash
python manage.py populate_cursos_gratuitos --verbose
```
**📁 Ubicación:** `cursos/management/commands/populate_cursos_gratuitos.py`

**Crea:**
- 6 cursos gratuitos para nuevos usuarios
- Cursos de introducción y conceptos básicos

#### 3.5 Poblar Usuarios de Prueba para Newsletter
```bash
python manage.py poblar_usuarios_newsletter --cantidad 10 --verbose
```
**📁 Ubicación:** `usuarios/management/commands/poblar_usuarios_newsletter.py`

**Crea:**
- Usuarios de prueba para testing de boletines
- Máximo 10 usuarios con datos realistas
- Útil para probar el sistema de newsletters

#### 3.6 Poblar Boletines de Prueba
```bash
python manage.py poblar_boletines --cantidad 10 --verbose
```
**📁 Ubicación:** `boletines/management/commands/poblar_boletines.py`

**Crea:**
- Boletines de ejemplo en diferentes categorías
- Contenido de prueba para el sistema de newsletters
- Diferentes estados: borrador, enviado, programado

---

## 🧹 PASO 4: Scripts de Limpieza (Opcional)

### Limpiar todos los datos
```bash
# ⚠️ CUIDADO: Esto borra TODOS los datos del sistema
python manage.py populate_master --action clean_all
```

### Verificar estado del sistema
```bash
python manage.py populate_master --action status
```

### Verificar usuarios del sistema
```bash
python manage.py check_users --verbose
```
**📁 Ubicación:** `usuarios/management/commands/check_users.py`

### Migrar usuarios específicos
```bash
python manage.py migrate_usuarios --verbose
```
**📁 Ubicación:** `usuarios/management/commands/migrate_usuarios.py`

---

## 📊 PASO 5: Verificación del Sistema

### 5.1 Verificar en el Admin
1. Ir a: `http://localhost:8000/admin/`
2. Iniciar sesión con el superusuario creado
3. Verificar que existan:
   - ✅ 3 Planes de membresía
   - ✅ 47+ Cursos (41 regulares + 6+ gratuitos)
   - ✅ 6 Categorías
   - ✅ 5 Tipos de consulta
   - ✅ Usuarios de prueba (si se poblaron)
   - ✅ Boletines de ejemplo (si se poblaron)

### 5.2 Verificar funcionalidad
```bash
# Ejecutar servidor de desarrollo
python manage.py runserver
```

Ir a: `http://localhost:8000/` y verificar que la página carga correctamente.

---

## 🎛️ Comandos Adicionales Útiles

### Forzar actualización de datos existentes
```bash
# Actualiza datos existentes en lugar de omitirlos
python manage.py populate_master --action complete --force
```

### Poblar componentes específicos
```bash
# Solo membresías
python manage.py populate_master --action membresias

# Solo cursos
python manage.py populate_master --action cursos

# Solo tipos de consulta
python manage.py populate_master --action tipos_consulta

# Solo cursos gratuitos  
python manage.py populate_master --action cursos_gratuitos
```

### Comandos adicionales individuales
```bash
# Poblar usuarios para newsletter
python manage.py poblar_usuarios_newsletter --cantidad 5

# Poblar boletines de prueba
python manage.py poblar_boletines --cantidad 8 --limpiar

# Limpiar y repoblar boletines
python manage.py limpiar_y_repoblar_boletines

# Verificar usuarios del sistema
python manage.py check_users

# Testing de emails (solo para desarrolladores)
python manage.py test_boletin_email
python manage.py test_contact_email
python manage.py test_envio_programado
```

---

## 📂 Estructura de Archivos de Poblado

```
usuarios/management/commands/
├── populate_master.py          # 🎯 Comando maestro
├── base_populate.py           # Base común para comandos
├── poblar_usuarios_newsletter.py # 👥 Usuarios para newsletter
├── check_users.py             # ✅ Verificar usuarios
└── migrate_usuarios.py        # 🔄 Migrar usuarios

membresias/management/commands/
├── populate_membresias.py     # 💳 Planes de membresía
└── populate_tipos_consulta.py # 💬 Tipos de consulta

cursos/management/commands/
├── populate_cursos.py         # 📚 Cursos principales
└── populate_cursos_gratuitos.py # 🆓 Cursos gratuitos

boletines/management/commands/
├── poblar_boletines.py        # 📰 Boletines de prueba
├── limpiar_y_repoblar_boletines.py # 🧹 Limpiar y repoblar
├── test_boletin_email.py      # ✉️ Test envío email
├── test_envio_programado.py   # ⏰ Test envío programado
└── test_feedback_programacion.py # 📊 Test feedback

blogs/management/commands/
└── test_contact_email.py      # ✉️ Test email contacto

# Scripts de migración automática
├── migration_master.ps1       # Windows PowerShell
├── migration_master.bat       # Windows CMD
└── migration_master.sh        # Linux/Mac

# Scripts de poblado automático
├── poblar_datos_master.ps1    # Windows PowerShell
├── poblar_datos_master.bat    # Windows CMD
└── poblar_datos_master.sh     # Linux/Mac
```

---

## 🚨 Solución de Problemas Comunes

### Error: "No hay usuarios staff"
```bash
# Crear superusuario si no existe
python manage.py createsuperuser
```

### Error: "Falta el plan de membresía"
```bash
# Ejecutar primero el poblado de membresías
python manage.py populate_membresias
```

### Error: "No hay categorías disponibles"
```bash
# Ejecutar primero el poblado de cursos
python manage.py populate_cursos
```

### Error de migración
```bash
# Reiniciar migraciones desde cero
python manage.py migrate --fake-initial
python manage.py makemigrations
python manage.py migrate
```

### Error 404 en `/account/login/` (Page not found)
**Problema:** Django-allauth a veces intenta redirigir a `/account/login/` (singular) pero el sistema usa `/accounts/` (plural).

**Solución:** Ya está implementada automáticamente. El sistema redirige:
- `/account/login/` → `/accounts/login/`
- `/account/logout/` → `/accounts/logout/`
- `/account/signup/` → `/accounts/signup/`

Si persiste el problema:
1. Reiniciar el servidor: `python manage.py runserver`
2. Limpiar caché del navegador
3. Verificar que `LOGIN_URL = "/accounts/login/"` esté en `settings.py`

---

## ⚡ Proceso Completo en 3 Comandos

### Opción A: Scripts automáticos (Windows)
```powershell
# 1. Migrar base de datos
.\migration_master.ps1

# 2. Crear superusuario
python manage.py createsuperuser

# 3. Poblar sistema completo
.\poblar_datos_master.ps1
```

### Opción B: Comandos manuales
```bash
# 1. Migrar base de datos
.\migration_master.ps1

# 2. Crear superusuario
python manage.py createsuperuser

# 3. Poblar sistema completo
python manage.py populate_master --action complete
```

---

## 📈 Resultado Final

Después de seguir todos los pasos, tendrás:

- ✅ Base de datos completamente migrada
- ✅ Superusuario administrativo creado
- ✅ 3 planes de membresía configurados
- ✅ 47+ cursos (41 regulares + 6+ gratuitos)
- ✅ 6 categorías de cursos
- ✅ 5 tipos de consultas por membresía
- ✅ Sistema de boletines funcional
- ✅ Usuarios de prueba para testing (opcional)
- ✅ Boletines de ejemplo (opcional)
- ✅ Sistema completamente funcional y navegable

---

## 📝 Notas Importantes

1. **Entorno de Desarrollo**: Este manual es para entorno de desarrollo
2. **Datos de Prueba**: Todos los datos creados son de prueba
3. **Contraseñas**: Cambiar contraseñas por defecto en producción
4. **Respaldos**: Hacer respaldo antes de ejecutar limpiezas
5. **Orden**: Respetar el orden de ejecución para evitar errores de dependencias
6. **Navegación**: El sistema incluye navegación completa (incluyendo "Boletines" en desktop y móvil)
7. **Testing**: Los comandos de testing (test_*) son solo para desarrolladores

---

**📅 Última actualización:** 10 de junio de 2025  
**👨‍💻 Autor:** Sistema de Poblado Automático  
**🔧 Versión:** 2.0.0  
**✨ Cambios recientes:**
- ✅ Agregados comandos para poblar usuarios y boletines de prueba
- ✅ Incluidos comandos de verificación y testing
- ✅ Documentada navegación completa (desktop y móvil)
- ✅ Agregados scripts automáticos de Windows (.ps1/.bat)
