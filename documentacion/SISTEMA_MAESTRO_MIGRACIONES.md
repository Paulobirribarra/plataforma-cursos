# 🔥 Sistema Maestro de Migraciones

## "Un script para dominarlas a todas" 💍

Este sistema automatizado resuelve completamente los problemas de migraciones al cambiar entre computadoras en proyectos Django.

## 🚀 Características

- **✅ Migración completa automatizada** - Ideal para cambio de PC
- **🔧 Comandos específicos por app** - Control granular
- **🧹 Limpieza automática** - Elimina migraciones conflictivas
- **📊 Estado en tiempo real** - Monitoreo de migraciones
- **🛡️ Confirmaciones de seguridad** - Protege contra operaciones destructivas
- **🌐 Multiplataforma** - PowerShell, BAT y Bash

## 📁 Estructura del Sistema

```
plataforma-cursos/
├── migration_master.ps1      # Script principal PowerShell
├── migration_master.bat      # Script Windows BAT  
├── migration_master.sh       # Script Unix/Linux Bash
├── plataforma_cursos/
│   └── management/commands/
│       ├── migrate_master.py # Comando Django maestro
│       └── base_migration.py # Clase base reutilizable
└── [app]/management/commands/
    └── migrate_[app].py      # Comando específico por app
```

## 🛠️ Scripts Disponibles

### 1. **PowerShell (Recomendado para Windows)**
```powershell
.\migration_master.ps1
```

### 2. **Windows BAT**
```cmd
migration_master.bat
```

### 3. **Unix/Linux Bash**
```bash
chmod +x migration_master.sh
./migration_master.sh
```

### 4. **Comando Django**
```bash
python manage.py migrate_master --action=complete
```

## 📋 Opciones Disponibles

| Opción | Descripción | Uso Recomendado |
|--------|-------------|-----------------|
| **🔄 Migración Completa** | Limpia + Crea + Aplica todas las migraciones | **Cambio de PC** |
| **📝 Solo Crear** | Genera archivos de migración | Desarrollo normal |
| **🚀 Solo Aplicar** | Ejecuta migraciones existentes | Deploy |
| **🧹 Limpiar** | Elimina archivos de migración | Reset de desarrollo |
| **🗄️ Reset Completo** | Flush DB + Migración completa | Desarrollo desde cero |
| **📊 Ver Estado** | Muestra status actual | Diagnóstico |

## 🎯 Flujo Recomendado para Cambio de PC

### En tu PC de trabajo (antes de subir a GitHub):
```bash
# 1. Commitear todo tu código
git add .
git commit -m "Avances del día"

# 2. Subir al repositorio
git push origin main
```

### En tu PC personal (después de bajar de GitHub):
```bash
# 1. Clonar o actualizar repositorio
git pull origin main

# 2. Activar entorno virtual
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate    # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar migración completa
.\migration_master.ps1
# Seleccionar opción 1: "MIGRACIÓN COMPLETA"
```

## 🔧 Comandos Django Específicos

### Comando Maestro
```bash
# Migración completa
python manage.py migrate_master --action=complete

# Solo crear migraciones
python manage.py migrate_master --action=create

# Solo aplicar migraciones
python manage.py migrate_master --action=apply

# Ver estado
python manage.py migrate_master --action=status
```

### Comandos por App
```bash
# Usuarios
python manage.py migrate_usuarios --action=create
python manage.py migrate_usuarios --action=apply

# Cursos
python manage.py migrate_cursos --action=clean

# Boletines
python manage.py migrate_boletines --action=status
```

## 🛡️ Seguridad y Respaldos

### Antes de operaciones destructivas:
- ✅ **Confirma respaldos** de tu base de datos
- ✅ **Commiteado todo** en Git
- ✅ **Variables de entorno** configuradas

### Operaciones peligrosas requieren confirmación:
- 🗑️ Limpiar migraciones (`s/N`)
- 💥 Reset completo (`s/N`)

## 🚨 Solución de Problemas Comunes

### Error: "No module named 'plataforma_cursos.management'"
```bash
# Verificar que existe la estructura:
plataforma_cursos/management/__init__.py
plataforma_cursos/management/commands/__init__.py
```

### Error: "No se encontró manage.py"
```bash
# Asegúrate de ejecutar desde la raíz del proyecto
cd e:\Paulo\Github\plataforma-cursos
.\migration_master.ps1
```

### Error de importación en comando base
```bash
# Verificar que Django encuentre el comando base
python manage.py help migrate_master
```

## 🎨 Personalización

### Agregar nueva app al sistema:
1. **Crear estructura de comandos:**
   ```bash
   mkdir nueva_app/management/commands
   touch nueva_app/management/__init__.py
   touch nueva_app/management/commands/__init__.py
   ```

2. **Crear comando específico:**
   ```python
   # nueva_app/management/commands/migrate_nueva_app.py
   from plataforma_cursos.management.commands.base_migration import AppMigrationCommand

   class Command(AppMigrationCommand):
       help = 'Comando específico para migraciones de nueva_app'
       app_name = 'nueva_app'
   ```

3. **Actualizar lista en scripts:**
   ```powershell
   # En migration_master.ps1
   $APPS = @("usuarios", "cursos", "nueva_app", "...")
   ```

## 📈 Ventajas del Sistema

| Antes | Después |
|-------|---------|
| ❌ Conflictos de migraciones | ✅ Limpieza automática |
| ❌ Comandos manuales repetitivos | ✅ Un comando para todo |
| ❌ Errores al cambiar de PC | ✅ Flujo automatizado |
| ❌ Sin control por app | ✅ Gestión granular |
| ❌ Sin feedback visual | ✅ Output colorizado |

## 🏆 Casos de Uso

- **🏠→💼 Trabajo → Casa:** Migración completa automática
- **👥 Equipo de desarrollo:** Sincronización consistente
- **🚀 Deploy a producción:** Aplicación controlada
- **🧪 Testing local:** Reset rápido de base de datos
- **🐛 Debug de migraciones:** Estado detallado por app

---

**💡 Tip:** Guarda este sistema como template para futuros proyectos Django. ¡Es completamente reutilizable!
