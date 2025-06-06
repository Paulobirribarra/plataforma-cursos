# 🚀 Guía Rápida - Sistema Maestro de Migraciones

## ⚡ Comandos Rápidos

### 🔄 Para cambio de PC (RECOMENDADO):
```powershell
.\migration_master.ps1
# Seleccionar opción 1
```

### 🐍 Desde Django:
```bash
python manage.py migrate_master --action=complete
```

### 📊 Ver estado:
```bash
python manage.py migrate_master --action=status
```

## 🛠️ Scripts Disponibles

| Script | Plataforma | Uso |
|--------|------------|-----|
| `migration_master.ps1` | Windows PowerShell | **RECOMENDADO** |
| `migration_master.bat` | Windows CMD | Alternativa CMD |
| `migration_master.sh` | Linux/Mac | Para sistemas Unix |

## 🎯 Comandos Django Específicos

### Comando Maestro:
```bash
python manage.py migrate_master --action=[complete|create|apply|clean|status|reset]
```

### Por App Individual:
```bash
python manage.py migrate_usuarios --action=[create|apply|clean|status]
python manage.py migrate_cursos --action=[create|apply|clean|status]
python manage.py migrate_pagos --action=[create|apply|clean|status]
python manage.py migrate_membresias --action=[create|apply|clean|status]
python manage.py migrate_blogs --action=[create|apply|clean|status]
python manage.py migrate_boletines --action=[create|apply|clean|status]
python manage.py migrate_carrito --action=[create|apply|clean|status]
```

## 🔥 Apps Configuradas

✅ **usuarios** - Gestión de usuarios y autenticación  
✅ **cursos** - Cursos y recursos educativos  
✅ **pagos** - Sistema de pagos Webpay  
✅ **membresias** - Planes de membresía  
✅ **blogs** - Publicaciones y contacto  
✅ **boletines** - Sistema de newsletters  
✅ **carrito** - Carrito de compras  

## 🛡️ Operaciones Seguras

- ✅ **Crear migraciones** - Seguro
- ✅ **Aplicar migraciones** - Seguro  
- ⚠️ **Limpiar migraciones** - Requiere confirmación
- 🚨 **Reset completo** - Requiere confirmación (elimina datos)

## 💡 Tips Rápidos

1. **Siempre usar migración completa** al cambiar de PC
2. **Hacer backup** antes de reset completo
3. **Commitear código** antes de operaciones destructivas
4. **Verificar .env** esté configurado correctamente

---
📖 Documentación completa: `documentacion/SISTEMA_MAESTRO_MIGRACIONES.md`
