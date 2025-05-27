# Script para migrar aplicaciones paso a paso
# filepath: e:\Paulo\Github\plataforma-cursos\migrate_apps.ps1

# Configuración inicial
$ErrorActionPreference = "Stop"
Write-Host "Iniciando migraciones paso a paso..." -ForegroundColor Green

# Verificar si el entorno virtual está activado
if (-not (Test-Path "env\Scripts\Activate.ps1")) {
    Write-Host "Error: El entorno virtual no existe. Crea uno con 'python -m venv env' y actívalo." -ForegroundColor Red
    exit 1
}

# Activar el entorno virtual
Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
. .\env\Scripts\Activate.ps1

Write-Host "=== MIGRACIONES PASO A PASO ===" -ForegroundColor Cyan

# Paso 1: Migrar dependencias de Django
Write-Host "1. Aplicando migraciones base de Django..." -ForegroundColor Yellow
python manage.py migrate contenttypes
python manage.py migrate auth
python manage.py migrate sessions
python manage.py migrate sites

# Paso 2: Migrar usuarios (base para otras apps)
Write-Host "2. Migrando aplicación 'usuarios'..." -ForegroundColor Yellow
python manage.py makemigrations usuarios
python manage.py migrate usuarios

# Paso 3: Migrar membresías (depende de usuarios)
Write-Host "3. Migrando aplicación 'membresias'..." -ForegroundColor Yellow
python manage.py makemigrations membresias
python manage.py migrate membresias

# Paso 4: Migrar cursos (depende de usuarios y membresías)
Write-Host "4. Migrando aplicación 'cursos'..." -ForegroundColor Yellow
python manage.py makemigrations cursos
python manage.py migrate cursos

# Paso 5: Migrar pagos (depende de usuarios)
Write-Host "5. Migrando aplicación 'pagos'..." -ForegroundColor Yellow
python manage.py makemigrations pagos
python manage.py migrate pagos

# Paso 6: Migrar carrito (depende de usuarios y cursos)
Write-Host "6. Migrando aplicación 'carrito'..." -ForegroundColor Yellow
python manage.py makemigrations carrito
python manage.py migrate carrito

# Paso 7: Aplicar cualquier migración restante
Write-Host "7. Aplicando migraciones restantes..." -ForegroundColor Yellow
python manage.py migrate

Write-Host "=== MIGRACIONES COMPLETADAS ===" -ForegroundColor Green
Write-Host "Todas las migraciones se han aplicado exitosamente." -ForegroundColor Green
Write-Host "Puedes crear un superusuario con: python manage.py createsuperuser" -ForegroundColor Yellow
