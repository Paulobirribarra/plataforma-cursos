# Script para reiniciar la base de datos y migraciones

# Configuración inicial
$ErrorActionPreference = "Stop"
Write-Host "Iniciando reinicio de la base de datos y migraciones..." -ForegroundColor Green

# Verificar si el entorno virtual está activado
if (-not (Test-Path "env\Scripts\Activate.ps1")) {
    Write-Host "Error: El entorno virtual no existe. Crea uno con 'python -m venv env' y actívalo." -ForegroundColor Red
    exit 1
}

# Paso 1: Activar el entorno virtual
Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
. .\env\Scripts\Activate.ps1

# Paso 2: Configurar contraseña de PostgreSQL
Write-Host "Configurando contraseña de PostgreSQL..." -ForegroundColor Yellow
$env:PGPASSWORD = "paulo12345"  # Usar la contraseña del archivo .env

# Paso 3: Terminar conexiones a la base de datos
Write-Host "Terminando conexiones a la base de datos 'plataforma_cursos'..." -ForegroundColor Yellow
try {
    psql -U postgres -h localhost -p 5432 -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'plataforma_cursos' AND pid <> pg_backend_pid();" -w
}
catch {
    Write-Host "Advertencia: No se pudieron terminar conexiones. Continuando..." -ForegroundColor Yellow
}

# Paso 4: Eliminar la base de datos
Write-Host "Eliminando base de datos 'plataforma_cursos'..." -ForegroundColor Yellow
psql -U postgres -h localhost -p 5432 -c "DROP DATABASE IF EXISTS plataforma_cursos;" -w

# Paso 5: Crear una nueva base de datos
Write-Host "Creando nueva base de datos 'plataforma_cursos'..." -ForegroundColor Yellow
psql -U postgres -h localhost -p 5432 -c "CREATE DATABASE plataforma_cursos;" -w

# Paso 6: Definir apps manualmente (más confiable que la detección automática)
Write-Host "Definiendo aplicaciones Django..." -ForegroundColor Yellow
$apps = @("usuarios", "cursos", "pagos", "membresias", "carrito")
Write-Host "Apps a procesar: $($apps -join ', ')" -ForegroundColor Cyan

# Paso 7: Eliminar migraciones de todas las apps propias
foreach ($app in $apps) {
    $migrationsPath = "$app\migrations"
    if (Test-Path $migrationsPath) {
        Get-ChildItem -Path $migrationsPath -Exclude "__init__.py" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        if (-not (Test-Path "$migrationsPath\__init__.py")) {
            New-Item -Path "$migrationsPath\__init__.py" -ItemType File -Force | Out-Null
        }
        Write-Host "Migraciones eliminadas para $app" -ForegroundColor Green
    }
    else {
        Write-Host "No se encontraron migraciones para $app. Saltando..." -ForegroundColor Yellow
    }
}

# Paso 8: Generar migraciones para aplicaciones propias (orden específico)
Write-Host "Generando migraciones en orden específico..." -ForegroundColor Yellow
$migrationOrder = @("usuarios", "membresias", "cursos", "pagos", "carrito")
foreach ($app in $migrationOrder) {
    Write-Host "Generando migración para $app..." -ForegroundColor Cyan
    python manage.py makemigrations $app
}

# Paso 9: Aplicar migraciones
Write-Host "Aplicando migraciones..." -ForegroundColor Yellow
python manage.py migrate

# Paso 10: Crear un superusuario automáticamente con datos más seguros
Write-Host "Creando superusuario 'admin'..." -ForegroundColor Yellow
try {
    $script = @"
from django.contrib.auth import get_user_model
import os
User = get_user_model()
if not User.objects.filter(email='admin@plataforma-cursos.local').exists():
    user = User.objects.create_superuser(
        email='admin@plataforma-cursos.local',
        password='Admin123!Dev',
        full_name='Administrador Sistema',
        username='admin'
    )
    print('Superusuario creado exitosamente')
else:
    print('El superusuario ya existe')
"@
    $script | python manage.py shell    Write-Host "Superusuario configurado:" -ForegroundColor Green
    Write-Host "  Email: admin@plataforma-cursos.local" -ForegroundColor Green
    Write-Host "  Password: Admin123!Dev" -ForegroundColor Green
    Write-Host "  Nombre: Administrador Sistema" -ForegroundColor Green
    
    # Verificar email del superusuario automáticamente
    Write-Host "Verificando email del superusuario..." -ForegroundColor Yellow
    $verifyScript = @"
from usuarios.models import CustomUser
try:
    superuser = CustomUser.objects.get(email='admin@plataforma-cursos.local', is_superuser=True)
    superuser.is_email_verified = True
    superuser.email_verification_token = None
    superuser.failed_login_attempts = 0
    superuser.account_locked_until = None
    superuser.save()
    print('✅ Email del superusuario verificado automáticamente')
except Exception as e:
    print(f'⚠️  Error al verificar email: {e}')
"@
    $verifyScript | python manage.py shell
}
catch {
    Write-Host "Error al crear superusuario. Créalo manualmente con 'python manage.py createsuperuser'." -ForegroundColor Red
    Write-Host "Comando sugerido: python manage.py createsuperuser --email admin@plataforma-cursos.local" -ForegroundColor Yellow
}

# Limpiar variable de entorno
Remove-Item -Path Env:\PGPASSWORD -ErrorAction SilentlyContinue

Write-Host "¡Reinicio completado! Base de datos y migraciones reiniciadas." -ForegroundColor Green
Write-Host "Puedes iniciar el servidor con: python manage.py runserver" -ForegroundColor Green