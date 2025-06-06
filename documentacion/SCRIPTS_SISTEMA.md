# 📋 Scripts del Sistema - Plataforma Cursos

## 🎯 Scripts Disponibles

### 🔥 Sistema Principal de Migraciones

#### `migration_master.ps1` (PowerShell - Windows)
**EL SCRIPT MAESTRO** - Administra todas las migraciones de forma automatizada.

**Opciones disponibles:**
1. **Migración Individual** - Migra una app específica
2. **Migración Paso a Paso** - Migra todas las apps en orden de dependencias
3. **Reset Completo** - Borra la BD y recrea desde cero
4. **Migración Completa** - Crea y aplica todas las migraciones
5. **Solo Crear Migraciones** - Genera archivos de migración sin aplicar
6. **Solo Aplicar Migraciones** - Aplica migraciones existentes
7. **Estado de Migraciones** - Muestra el estado actual

**Uso:**
```powershell
.\migration_master.ps1
```

#### `migration_master.bat` (Windows CMD)
Versión para línea de comandos de Windows.

#### `migration_master.sh` (Unix/Linux/Mac)
Versión para sistemas Unix.

### 🎭 Sistema Principal de Poblado

#### `poblar_datos_master.ps1` (PowerShell - Windows)
**EL SCRIPT MAESTRO DE DATOS** - Administra todo el poblado de datos de forma automatizada.

**Opciones disponibles:**
1. **Poblado Completo** - Crea todos los datos del sistema en orden
2. **Solo Membresías** - Crea planes de membresía (Básico, Intermedio, Premium)
3. **Solo Cursos** - Crea cursos, categorías y tags
4. **Solo Tipos de Consulta** - Configura tipos de asesorías y consultas
5. **Solo Cursos Gratuitos** - Crea cursos gratuitos específicos
6. **Limpiar Todos los Datos** - ¡CUIDADO! Borra todos los datos de poblado
7. **Estado Actual** - Muestra estadísticas de datos existentes

**Uso:**
```powershell
.\poblar_datos_master.ps1
```

#### `poblar_datos_master.bat` (Windows CMD)
Versión para línea de comandos de Windows.

#### `poblar_datos_master.sh` (Unix/Linux/Mac)
Versión para sistemas Unix.

### 🧪 Scripts Auxiliares

#### `ejecutar_pruebas.ps1`
Script simple para ejecutar todas las pruebas del sistema.
```powershell
.\ejecutar_pruebas.ps1
```

#### `poblar_datos.ps1` (DEPRECATED)
⚠️ **DEPRECATED** - Usar `poblar_datos_master.ps1` en su lugar.
```powershell
.\poblar_datos.ps1
```

## 🎮 Comandos Django Integrados

### Comando Maestro de Migraciones
```bash
python manage.py migrate_master --action=complete
```

### Comando Maestro de Poblado
```bash
python manage.py populate_master --action=complete
```

### Comandos por App - Migraciones
```bash
python manage.py migrate_usuarios
python manage.py migrate_cursos
python manage.py migrate_pagos
python manage.py migrate_membresias
python manage.py migrate_blogs
python manage.py migrate_boletines
python manage.py migrate_carrito
```

### Comandos por App - Poblado
```bash
python manage.py populate_membresias
python manage.py populate_cursos
python manage.py populate_tipos_consulta
python manage.py populate_cursos_gratuitos
```

## 🗂️ Arquitectura de Comandos

```
usuarios/management/commands/
├── base_migration.py      # Clase base para migraciones
├── base_populate.py       # Clase base para poblado
├── migrate_master.py      # Comando maestro migraciones
├── populate_master.py     # Comando maestro poblado
└── migrate_usuarios.py    # Comando específico usuarios

cursos/management/commands/
├── migrate_cursos.py      # Comando específico cursos
├── populate_cursos.py     # Poblado de cursos
└── populate_cursos_gratuitos.py  # Poblado cursos gratuitos

membresias/management/commands/
├── populate_membresias.py         # Poblado de membresías
└── populate_tipos_consulta.py     # Poblado tipos consulta

[...otros apps...]
```

## 🚀 Flujo Recomendado

### Para desarrollo diario:
```powershell
# Migraciones
.\migration_master.ps1
# Seleccionar opción 4 (Migración Completa)

# Poblado de datos
.\poblar_datos_master.ps1
# Seleccionar opción 1 (Poblado Completo)
```

### Para nuevo setup en otra computadora:
```powershell
# 1. Clonar repositorio
git clone [url]

# 2. Crear entorno virtual
python -m venv env

# 3. Activar entorno
.\env\Scripts\Activate.ps1

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Configurar .env (copiar de .env.example)

# 6. Ejecutar migración completa
.\migration_master.ps1
# Seleccionar opción 3 (Reset Completo)

# 7. Poblar datos de prueba
.\poblar_datos_master.ps1
# Seleccionar opción 1 (Poblado Completo)
```

### Para poblar datos específicos:
```powershell
# Solo cursos gratuitos
.\poblar_datos_master.ps1
# Seleccionar opción 5

# Solo membresías
.\poblar_datos_master.ps1
# Seleccionar opción 2
```

## ⚡ Características del Sistema

### 🔥 Sistema de Migraciones
- ✅ **Multiplataforma** - Scripts para Windows, Linux y Mac
- ✅ **Auto-diagnóstico** - Verifica entorno antes de ejecutar
- ✅ **Manejo de errores** - Rollback automático si algo falla
- ✅ **Orden de dependencias** - Respeta las relaciones entre apps
- ✅ **Interfaz amigable** - Menús interactivos y colores
- ✅ **Integración Django** - Comandos nativos disponibles
- ✅ **Arquitectura reutilizable** - Clase base para nuevos comandos

### 🎭 Sistema de Poblado
- ✅ **Datos consistentes** - Crea datos coherentes entre tablas
- ✅ **Transacciones seguras** - Rollback automático en caso de error
- ✅ **Validación de dependencias** - Verifica que existan datos requeridos
- ✅ **Estadísticas en tiempo real** - Muestra contadores de creación
- ✅ **Modo verbose** - Información detallada opcional
- ✅ **Limpieza selectiva** - Borrar solo datos específicos
- ✅ **Planes de membresía** - 3 niveles (Básico, Intermedio, Premium)
- ✅ **Cursos gratuitos** - Lead magnets para atraer usuarios

## 🔧 Solución de Problemas

### Error de permisos:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error de base de datos:
```powershell
# Usar opción 3 (Reset Completo)
.\migration_master.ps1
```

### Agregar nueva app:
1. Agregar el nombre a la lista `$APPS` en `migration_master.ps1`
2. Crear comando específico usando `base_migration.py` como plantilla

---
**💡 Tip:** Siempre usa el sistema maestro en lugar de comandos manuales para garantizar consistencia.
