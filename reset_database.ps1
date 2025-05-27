# Script para reiniciar la base de datos y migraciones

# Configuración inicial
$ErrorActionPreference = "Stop"
Write-Host "Iniciando reinicio de la base de datos y migraciones..." -ForegroundColor Green

# Verificar si el entorno virtual está activado
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "Error: El entorno virtual no existe. Crea uno con 'python -m venv venv' y actívalo." -ForegroundColor Red
    exit 1
}

# Paso 1: Activar el entorno virtual
Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
. .\venv\Scripts\Activate.ps1

# Paso 2: Configurar contraseña de PostgreSQL
Write-Host "Configurando contraseña de PostgreSQL..." -ForegroundColor Yellow
$env:PGPASSWORD = "paulo12345"  # Cambia esto en producción o usa una variable de entorno

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

# Paso 6: Detectar todas las apps propias (carpetas con __init__.py y migrations)
Write-Host "Detectando apps propias..." -ForegroundColor Yellow
$apps = Get-ChildItem -Directory | Where-Object {
    Test-Path "$($_.FullName)\__init__.py" -or Test-Path "$($_.FullName)\apps.py"
} | Where-Object {
    Test-Path "$($_.FullName)\migrations"
} | ForEach-Object { $_.Name }

Write-Host "Apps detectadas: $($apps -join ', ')" -ForegroundColor Cyan

# Paso 7: Eliminar migraciones de todas las apps propias
foreach ($app in $apps) {
    $migrationsPath = "$app\migrations"
    if (Test-Path $migrationsPath) {
        Get-ChildItem -Path $migrationsPath -Exclude "__init__.py" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        if (-not (Test-Path "$migrationsPath\__init__.py")) {
            New-Item -Path "$migrationsPath\__init__.py" -ItemType File -Force | Out-Null
        }
        Write-Host "Migraciones eliminadas para $app" -ForegroundColor Green
    } else {
        Write-Host "No se encontraron migraciones para $app. Saltando..." -ForegroundColor Yellow
    }
}

# Paso 8: Verificar importaciones antes de generar migraciones
Write-Host "Verificando importaciones..." -ForegroundColor Yellow
try {
    $importScript = ($apps | ForEach-Object { "from $($_).models import *;" }) -join " "
    $importScript += " print('Importaciones correctas')"
    Write-Output $importScript | python manage.py shell
}
catch {
    Write-Host "Error: Problemas con las importaciones. Corrige los modelos antes de continuar." -ForegroundColor Red
    exit 1
}

# Paso 9: Generar nuevas migraciones para todas las apps propias
Write-Host "Generando nuevas migraciones..." -ForegroundColor Yellow
python manage.py makemigrations $($apps -join " ")

# Paso 10: Aplicar migraciones
Write-Host "Aplicando migraciones..." -ForegroundColor Yellow
python manage.py migrate

# Paso 11: Crear un superusuario automáticamente
Write-Host "Creando superusuario 'admin'..." -ForegroundColor Yellow
try {
    $script = "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin@example.com', 'admin12345')"
    Write-Output $script | python manage.py shell
    Write-Host "Superusuario creado: email=admin@example.com, password=admin12345" -ForegroundColor Green
}
catch {
    Write-Host "Error al crear superusuario. Crea uno manualmente con 'python manage.py createsuperuser'." -ForegroundColor Red
}

# Limpiar variable de entorno
Remove-Item -Path Env:\PGPASSWORD -ErrorAction SilentlyContinue

Write-Host "¡Reinicio completado! Base de datos y migraciones reiniciadas." -ForegroundColor Green
Write-Host "Puedes iniciar el servidor con: python manage.py runserver" -ForegroundColor Green