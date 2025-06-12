# ================================
# SISTEMA MAESTRO DE MIGRACIONES
# ================================
# Un script para dominarlas a todas 💍
# Autor: Paulo - Plataforma Cursos
# Fecha: Junio 2025

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "🔥 SISTEMA MAESTRO DE MIGRACIONES 🔥" -ForegroundColor Yellow
Write-Host "Un script para dominarlas a todas 💍" -ForegroundColor Green  
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Configuración
$APPS = @("usuarios", "cursos", "pagos", "membresias", "blogs", "boletines", "carrito")
$PYTHON_CMD = "python"
$MANAGE_PY = "manage.py"

# Funciones auxiliares
function Write-Step {
    param($Message, $Color = "White")
    Write-Host "⚡ $Message" -ForegroundColor $Color
}

function Write-Success {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Warning {
    param($Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Test-PythonAndDjango {
    Write-Step "Verificando entorno Python y Django..." "Cyan"
    
    try {
        $pythonVersion = & $PYTHON_CMD --version 2>&1
        Write-Success "Python detectado: $pythonVersion"
    }
    catch {
        Write-Error "Python no encontrado. Asegúrate de tener Python instalado y en el PATH."
        return $false
    }
    
    try {
        & $PYTHON_CMD $MANAGE_PY --version 2>&1 | Out-Null
        Write-Success "Django proyecto detectado correctamente"
        return $true
    }
    catch {
        Write-Error "No se pudo ejecutar manage.py. Verifica que estés en el directorio correcto."
        return $false
    }
}

function Remove-AllMigrations {
    Write-Step "🧹 Limpiando migraciones existentes..." "Yellow"
    
    foreach ($app in $APPS) {
        $migrationsPath = "$app/migrations"
        if (Test-Path $migrationsPath) {
            Write-Step "Limpiando migraciones de $app" "Gray"
            Get-ChildItem "$migrationsPath/*.py" | Where-Object { $_.Name -ne "__init__.py" } | Remove-Item -Force
            Write-Success "Migraciones de $app eliminadas"
        } else {
            Write-Warning "No se encontró carpeta de migraciones para $app"
        }
    }
    Write-Success "✨ Limpieza de migraciones completada"
}

function Reset-Database {
    Write-Step "🗄️  Reseteando base de datos..." "Red"
    
    try {
        Write-Step "Eliminando y recreando la base de datos..."
        & $PYTHON_CMD $MANAGE_PY flush --noinput 2>&1 | Out-Null
        Write-Success "Base de datos reseteada"
    }
    catch {
        Write-Warning "No se pudo hacer flush de la base de datos (puede ser normal en primera ejecución)"
    }
}

function Create-MigrationsForApp {
    param($AppName)
    
    Write-Step "📝 Creando migraciones para $AppName..." "Blue"
    
    try {
        $output = & $PYTHON_CMD $MANAGE_PY makemigrations $AppName 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Migraciones creadas para $AppName"
            return $true
        } else {
            Write-Error "Error creando migraciones para $AppName`: $output"
            return $false
        }
    }
    catch {
        Write-Error "Excepción al crear migraciones para $AppName`: $($_.Exception.Message)"
        return $false
    }
}

function Apply-MigrationsForApp {
    param($AppName)
    
    Write-Step "🚀 Aplicando migraciones para $AppName..." "Green"
    
    try {
        $output = & $PYTHON_CMD $MANAGE_PY migrate $AppName 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Migraciones aplicadas para $AppName"
            return $true
        } else {
            Write-Error "Error aplicando migraciones para $AppName`: $output"
            return $false
        }
    }
    catch {
        Write-Error "Excepción al aplicar migraciones para $AppName`: $($_.Exception.Message)"
        return $false
    }
}

function Show-Menu {
    Write-Host ""
    Write-Host "===================== OPCIONES =====================" -ForegroundColor Cyan
    Write-Host "1. 🔄 MIGRACIÓN COMPLETA (Recomendado para cambio de PC)" -ForegroundColor Green
    Write-Host "2. 📝 Solo crear migraciones (sin aplicar)" -ForegroundColor Blue  
    Write-Host "3. 🚀 Solo aplicar migraciones existentes" -ForegroundColor Yellow
    Write-Host "4. 🧹 Limpiar todas las migraciones" -ForegroundColor Red
    Write-Host "5. 🗄️  Reset completo de base de datos + migraciones" -ForegroundColor Magenta
    Write-Host "6. ℹ️  Ver estado actual de migraciones" -ForegroundColor White
    Write-Host "7. 🚪 Salir" -ForegroundColor Gray
    Write-Host "====================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Show-MigrationStatus {
    Write-Step "📊 Estado actual de migraciones..." "Cyan"
    
    try {
        Write-Host ""
        Write-Host "--- MIGRACIONES PENDIENTES ---" -ForegroundColor Yellow
        & $PYTHON_CMD $MANAGE_PY showmigrations --plan
        Write-Host ""
        Write-Host "--- ESTADO POR APP ---" -ForegroundColor Yellow  
        & $PYTHON_CMD $MANAGE_PY showmigrations
    }
    catch {
        Write-Error "Error al mostrar estado de migraciones"
    }
}

function Complete-Migration {
    Write-Step "🎯 INICIANDO MIGRACIÓN COMPLETA..." "Magenta"
    
    if (-not (Test-PythonAndDjango)) {
        return
    }
    
    # Paso 1: Limpiar migraciones
    Remove-AllMigrations
    
    # Paso 2: Crear migraciones para cada app
    Write-Step "📝 Creando nuevas migraciones..." "Blue"
    $allSuccessful = $true
    
    foreach ($app in $APPS) {
        if (-not (Create-MigrationsForApp $app)) {
            $allSuccessful = $false
        }
        Start-Sleep -Milliseconds 500  # Pequeña pausa entre apps
    }
    
    if (-not $allSuccessful) {
        Write-Error "Algunos errores al crear migraciones. Revisa los logs arriba."
        return
    }
    
    # Paso 3: Aplicar migraciones
    Write-Step "🚀 Aplicando todas las migraciones..." "Green"
    
    try {
        Write-Step "Aplicando migraciones del sistema..."
        & $PYTHON_CMD $MANAGE_PY migrate 
        Write-Success "✨ MIGRACIÓN COMPLETA EXITOSA ✨"
    }
    catch {
        Write-Error "Error en la aplicación final de migraciones"
    }
}

# ============= PROGRAMA PRINCIPAL =============

# Verificar que estamos en el directorio correcto
if (-not (Test-Path $MANAGE_PY)) {
    Write-Error "No se encontró manage.py. Asegúrate de estar en el directorio raíz del proyecto Django."
    exit 1
}

# Loop principal del menú
do {
    Show-Menu
    $choice = Read-Host "Selecciona una opción (1-7)"
    
    switch ($choice) {
        "1" {
            Complete-Migration
        }
        "2" {
            if (Test-PythonAndDjango) {
                foreach ($app in $APPS) {
                    Create-MigrationsForApp $app
                }
            }
        }
        "3" {
            if (Test-PythonAndDjango) {
                Write-Step "🚀 Aplicando todas las migraciones..."
                & $PYTHON_CMD $MANAGE_PY migrate
            }
        }
        "4" {
            $confirm = Read-Host "⚠️  ¿Estás seguro de que quieres limpiar TODAS las migraciones? (s/N)"
            if ($confirm -eq "s" -or $confirm -eq "S") {
                Remove-AllMigrations
            }
        }
        "5" {
            $confirm = Read-Host "⚠️  ¿Estás seguro de que quieres hacer un RESET COMPLETO? (s/N)"
            if ($confirm -eq "s" -or $confirm -eq "S") {
                Reset-Database
                Remove-AllMigrations
                Complete-Migration
            }
        }
        "6" {
            Show-MigrationStatus
        }
        "7" {
            Write-Success "👋 ¡Hasta luego!"
            break
        }
        default {
            Write-Warning "Opción no válida. Selecciona del 1 al 7."
        }
    }
    
    if ($choice -ne "7") {
        Write-Host ""
        Read-Host "Presiona Enter para continuar..."
        Clear-Host
    }
    
} while ($choice -ne "7")

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "🎉 Script de migraciones finalizado" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan
