# ================================
# SISTEMA MAESTRO DE POBLADO DE DATOS
# ================================
# El hermano del sistema maestro de migraciones 👥
# Autor: Paulo - Plataforma Cursos
# Fecha: Junio 2025

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "🎭 SISTEMA MAESTRO DE POBLADO DE DATOS 🎭" -ForegroundColor Yellow
Write-Host "El hermano del sistema de migraciones 👥" -ForegroundColor Green  
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Configuración
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
        & $PYTHON_CMD $MANAGE_PY check --deploy 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Django configurado correctamente"
        } else {
            Write-Warning "Django con advertencias de configuración, pero funcional"
        }
    }
    catch {
        Write-Error "Error verificando Django. Asegúrate de estar en el directorio del proyecto."
        return $false
    }
    
    return $true
}

function Show-Menu {
    Write-Host ""
    Write-Host "🎯 OPCIONES DISPONIBLES:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. 🎉 Poblado Completo" -ForegroundColor Green
    Write-Host "   └─ Crea todos los datos del sistema en orden"
    Write-Host ""
    Write-Host "2. 💎 Solo Membresías" -ForegroundColor Cyan
    Write-Host "   └─ Crea planes de membresía (Básico, Intermedio, Premium)"
    Write-Host ""
    Write-Host "3. 📚 Solo Cursos" -ForegroundColor Blue
    Write-Host "   └─ Crea cursos, categorías y tags"
    Write-Host ""
    Write-Host "4. 📋 Solo Tipos de Consulta" -ForegroundColor Magenta
    Write-Host "   └─ Configura tipos de asesorías y consultas"
    Write-Host ""
    Write-Host "5. 🆓 Solo Cursos Gratuitos" -ForegroundColor White
    Write-Host "   └─ Crea cursos gratuitos específicos"
    Write-Host ""
    Write-Host "6. 🧹 Limpiar Todos los Datos" -ForegroundColor Red
    Write-Host "   └─ ¡CUIDADO! Borra todos los datos de poblado"
    Write-Host ""
    Write-Host "7. 📊 Estado Actual" -ForegroundColor DarkYellow
    Write-Host "   └─ Muestra estadísticas de datos existentes"
    Write-Host ""
    Write-Host "8. 🚪 Salir" -ForegroundColor Gray
    Write-Host ""
}

function Execute-PopulateCommand {
    param(
        [string]$Action,
        [string]$Description
    )
    
    Write-Step "Ejecutando: $Description" "Cyan"
    
    try {
        & $PYTHON_CMD $MANAGE_PY populate_master --action=$Action
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "¡$Description completado exitosamente!"
            return $true
        } else {
            Write-Error "Error ejecutando $Description"
            return $false
        }
    }
    catch {
        Write-Error "Excepción ejecutando $Description`: $($_.Exception.Message)"
        return $false
    }
}

function Show-PostExecution-Tips {
    param([string]$Action)
    
    Write-Host ""
    Write-Host "💡 CONSEJOS POST-EJECUCIÓN:" -ForegroundColor Yellow
    
    switch ($Action) {
        "complete" {
            Write-Host "   • Verifica los datos creados en el admin de Django" -ForegroundColor White
            Write-Host "   • Los cursos gratuitos están marcados como destacados" -ForegroundColor White
            Write-Host "   • Los planes de membresía están listos para asignar" -ForegroundColor White
        }
        "membresias" {
            Write-Host "   • Ahora puedes crear usuarios y asignarles planes" -ForegroundColor White
            Write-Host "   • Los planes incluyen diferentes niveles de acceso" -ForegroundColor White
        }
        "cursos" {
            Write-Host "   • Los cursos están listos para ser publicados" -ForegroundColor White
            Write-Host "   • Puedes agregar contenido y lecciones" -ForegroundColor White
        }
        "tipos_consulta" {
            Write-Host "   • Los tipos de consulta están vinculados a planes de membresía" -ForegroundColor White
            Write-Host "   • Usuarios premium tienen acceso a consultas individuales" -ForegroundColor White
        }
        "cursos_gratuitos" {
            Write-Host "   • Perfectos como 'lead magnets' para atraer nuevos usuarios" -ForegroundColor White
            Write-Host "   • Los destacados aparecerán en la página principal" -ForegroundColor White
        }
        "status" {
            Write-Host "   • Usa esta opción regularmente para monitorear el sistema" -ForegroundColor White
        }
    }
    
    Write-Host "   • Admin Django: http://localhost:8000/admin/" -ForegroundColor Green
    Write-Host "   • Para crear superusuario: python manage.py createsuperuser" -ForegroundColor Green
}

# =====================================
# FLUJO PRINCIPAL
# =====================================

# Verificar entorno
if (-not (Test-PythonAndDjango)) {
    Write-Error "El entorno no está configurado correctamente. Abortando."
    exit 1
}

# Loop principal del menú
do {
    Show-Menu
    
    $choice = Read-Host "Selecciona una opción (1-8)"
    
    Write-Host ""
    Write-Host "=" * 50 -ForegroundColor DarkGray
    
    $success = $false
    $action = ""
    
    switch ($choice) {
        "1" {
            $action = "complete"
            $success = Execute-PopulateCommand "complete" "Poblado Completo del Sistema"
        }
        "2" {
            $action = "membresias"
            $success = Execute-PopulateCommand "membresias" "Poblado de Membresías"
        }
        "3" {
            $action = "cursos"
            $success = Execute-PopulateCommand "cursos" "Poblado de Cursos"
        }
        "4" {
            $action = "tipos_consulta"
            $success = Execute-PopulateCommand "tipos_consulta" "Poblado de Tipos de Consulta"
        }
        "5" {
            $action = "cursos_gratuitos"
            $success = Execute-PopulateCommand "cursos_gratuitos" "Poblado de Cursos Gratuitos"
        }
        "6" {
            Write-Warning "¡ATENCIÓN! Esta acción eliminará TODOS los datos de poblado."
            $confirm = Read-Host "¿Estás seguro? Escribe 'CONFIRMAR' para continuar"
            
            if ($confirm -eq "CONFIRMAR") {
                $action = "clean_all"
                $success = Execute-PopulateCommand "clean_all" "Limpieza de Todos los Datos"
            } else {
                Write-Host "Operación cancelada." -ForegroundColor Yellow
                $success = $true  # Para no mostrar error
            }
        }
        "7" {
            $action = "status"
            $success = Execute-PopulateCommand "status" "Estado Actual del Sistema"
        }
        "8" {
            Write-Host "¡Hasta luego! 👋" -ForegroundColor Green
            exit 0
        }
        default {
            Write-Warning "Opción inválida. Por favor selecciona entre 1-8."
            continue
        }
    }
    
    if ($success -and $action -ne "") {
        Show-PostExecution-Tips $action
    }
    
    Write-Host ""
    Write-Host "=" * 50 -ForegroundColor DarkGray
    Write-Host ""
    
    if ($choice -ne "8") {
        $continue = Read-Host "¿Deseas realizar otra acción? (s/n)"
        if ($continue.ToLower() -ne "s") {
            Write-Host "¡Gracias por usar el Sistema Maestro de Poblado! 🎭" -ForegroundColor Green
            break
        }
    }
    
} while ($true)
