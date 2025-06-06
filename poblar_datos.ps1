# ===============================================
# ⚠️  SCRIPT DEPRECATED - USAR poblar_datos_master.ps1
# ===============================================
# Este script está obsoleto. Usa el nuevo sistema maestro:
# .\poblar_datos_master.ps1
# 
# El nuevo sistema incluye:
# - Interfaz interactiva
# - Mejor manejo de errores
# - Comandos Django integrados
# - Poblado selectivo
# - Estadísticas en tiempo real
# ===============================================

Write-Host "⚠️  ADVERTENCIA: Este script está DEPRECATED" -ForegroundColor Yellow
Write-Host "🔥 Usa el nuevo sistema maestro: .\poblar_datos_master.ps1" -ForegroundColor Green
Write-Host ""

$response = Read-Host "¿Deseas continuar con el script antiguo? (s/n)"
if ($response.ToLower() -ne "s") {
    Write-Host "👍 Redirigiendo al nuevo sistema..." -ForegroundColor Green
    Start-Sleep 2
    
    if (Test-Path "poblar_datos_master.ps1") {
        & ".\poblar_datos_master.ps1"
    } else {
        Write-Host "❌ No se encontró poblar_datos_master.ps1" -ForegroundColor Red
    }
    exit 0
}

Write-Host "⚠️  Continuando con script antiguo..." -ForegroundColor Yellow
Write-Host ""

# Script para poblar la base de datos con datos de ejemplo
# Ejecuta los scripts de población en el orden correcto

Write-Host "🚀 Iniciando población de la base de datos..." -ForegroundColor Green

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "manage.py")) {
    Write-Host "❌ Error: No se encuentra manage.py. Ejecuta este script desde el directorio raíz del proyecto." -ForegroundColor Red
    exit 1
}

# Activar el entorno virtual
Write-Host "📦 Activando entorno virtual..." -ForegroundColor Yellow
try {
    & "env\Scripts\Activate.ps1"
    Write-Host "✅ Entorno virtual activado" -ForegroundColor Green
}
catch {
    Write-Host "❌ Error al activar el entorno virtual. Asegúrate de que existe la carpeta 'env'." -ForegroundColor Red
    exit 1
}

# Verificar que el servidor esté configurado correctamente
Write-Host "🔍 Verificando configuración..." -ForegroundColor Yellow
$checkResult = python manage.py check --deploy
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Hay problemas de configuración, pero continuando..." -ForegroundColor Yellow
}

# 1. Poblar membresías primero (los cursos pueden requerirlas)
Write-Host "`n📊 Creando planes de membresía..." -ForegroundColor Cyan
try {
    python scripts\poblar_membresias.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Planes de membresía creados exitosamente" -ForegroundColor Green
    }
    else {
        Write-Host "❌ Error al crear planes de membresía" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "❌ Error al ejecutar poblar_membresias.py: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 2. Poblar cursos
Write-Host "`n📚 Creando cursos..." -ForegroundColor Cyan
try {
    python scripts\poblar_cursos.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Cursos creados exitosamente" -ForegroundColor Green
    }
    else {
        Write-Host "❌ Error al crear cursos" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "❌ Error al ejecutar poblar_cursos.py: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Mostrar resumen
Write-Host "`n📈 Resumen de la población:" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

$summaryScript = @"
from membresias.models import MembershipPlan
from cursos.models import Course, Category, Tag
from usuarios.models import CustomUser

print(f'👥 Usuarios totales: {CustomUser.objects.count()}')
print(f'📊 Planes de membresía: {MembershipPlan.objects.count()}')
print(f'📚 Cursos totales: {Course.objects.count()}')
print(f'🏷️  Categorías: {Category.objects.count()}')
print(f'🏷️  Etiquetas: {Tag.objects.count()}')
print(f'🆓 Cursos gratuitos: {Course.objects.filter(is_free=True).count()}')
print(f'💰 Cursos de pago: {Course.objects.filter(is_free=False).count()}')
"@

$summaryScript | python manage.py shell

Write-Host "`n🎉 ¡Base de datos poblada exitosamente!" -ForegroundColor Green
Write-Host "Puedes iniciar el servidor con: python manage.py runserver" -ForegroundColor Green
Write-Host "Y acceder al admin en: http://127.0.0.1:8000/admin/" -ForegroundColor Green
Write-Host "Usuario: admin@plataforma-cursos.local | Password: Admin123!Dev" -ForegroundColor Yellow
