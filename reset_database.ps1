# Script para reiniciar la base de datos y migraciones de la plataforma de cursos

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
.\venv\Scripts\Activate.ps1

# Paso 2: Configurar contraseña de PostgreSQL
Write-Host "Configurando contraseña de PostgreSQL..." -ForegroundColor Yellow
$env:PGPASSWORD = "root"  # Cambia esto en producción o usa una variable de entorno

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

# Paso 6: Eliminar migraciones de todas las apps propias
Write-Host "Eliminando migraciones de todas las apps propias..." -ForegroundColor Yellow
$apps = @("cursos", "usuarios", "pagos")  # Añade aquí todas tus apps propias
foreach ($app in $apps) {
     $migrationsPath = "$app\migrations"
     if (Test-Path $migrationsPath) {
          Remove-Item -Path $migrationsPath -Recurse -Force -ErrorAction SilentlyContinue
          New-Item -Path $migrationsPath -ItemType Directory -Force
          New-Item -Path "$migrationsPath\__init__.py" -ItemType File -Force
          Write-Host "Migraciones eliminadas para $app" -ForegroundColor Green
     }
     else {
          Write-Host "No se encontraron migraciones para $app. Saltando..." -ForegroundColor Yellow
     }
}

# Paso 7: Generar nuevas migraciones
Write-Host "Generando nuevas migraciones..." -ForegroundColor Yellow
python manage.py makemigrations

# Paso 8: Aplicar migraciones
Write-Host "Aplicando migraciones..." -ForegroundColor Yellow
python manage.py migrate

# Paso 9: Crear un superusuario automáticamente
Write-Host "Creando superusuario 'admin'..." -ForegroundColor Yellow
try {
     $script = "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin12345')"
     Write-Output $script | python manage.py shell
}
catch {
     Write-Host "Error al crear superusuario. Crea uno manualmente con 'python manage.py createsuperuser'." -ForegroundColor Red
}

# Limpiar variable de entorno
Remove-Item -Path Env:\PGPASSWORD -ErrorAction SilentlyContinue

Write-Host "¡Reinicio completado! Base de datos y migraciones reiniciadas." -ForegroundColor Green
Write-Host "Superusuario creado: username=admin, email=admin@example.com, password=admin12345" -ForegroundColor Green
Write-Host "Puedes iniciar el servidor con: python manage.py runserver" -ForegroundColor Green