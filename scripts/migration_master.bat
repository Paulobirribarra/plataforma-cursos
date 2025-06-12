@echo off
REM ================================
REM SISTEMA MAESTRO DE MIGRACIONES
REM ================================
REM Un script para dominarlas a todas (Versión Windows BAT)
REM Autor: Paulo - Plataforma Cursos

echo ===============================================
echo     🔥 SISTEMA MAESTRO DE MIGRACIONES 🔥
echo     Un script para dominarlas a todas 💍
echo ===============================================
echo.

:menu
echo ===================== OPCIONES =====================
echo 1. 🔄 MIGRACIÓN COMPLETA (Recomendado para cambio de PC)
echo 2. 📝 Solo crear migraciones (sin aplicar)
echo 3. 🚀 Solo aplicar migraciones existentes
echo 4. 🧹 Limpiar todas las migraciones
echo 5. 🗄️  Reset completo de base de datos + migraciones
echo 6. ℹ️  Ver estado actual de migraciones
echo 7. 🚪 Salir
echo ====================================================
echo.

set /p choice="Selecciona una opción (1-7): "

if "%choice%"=="1" goto complete_migration
if "%choice%"=="2" goto create_migrations
if "%choice%"=="3" goto apply_migrations
if "%choice%"=="4" goto clean_migrations
if "%choice%"=="5" goto reset_complete
if "%choice%"=="6" goto show_status
if "%choice%"=="7" goto exit
goto invalid_option

:complete_migration
echo 🎯 Ejecutando migración completa...
python manage.py migrate_master --action=complete
goto pause_and_menu

:create_migrations
echo 📝 Creando migraciones...
python manage.py migrate_master --action=create
goto pause_and_menu

:apply_migrations
echo 🚀 Aplicando migraciones...
python manage.py migrate_master --action=apply
goto pause_and_menu

:clean_migrations
set /p confirm="⚠️  ¿Estás seguro de limpiar TODAS las migraciones? (s/N): "
if /i "%confirm%"=="s" (
    python manage.py migrate_master --action=clean
)
goto pause_and_menu

:reset_complete
echo ⚠️  ATENCIÓN: Esto eliminará TODOS los datos de la base de datos
set /p confirm="¿Estás completamente seguro? (s/N): "
if /i "%confirm%"=="s" (
    python manage.py migrate_master --action=reset
)
goto pause_and_menu

:show_status
echo 📊 Mostrando estado de migraciones...
python manage.py migrate_master --action=status
goto pause_and_menu

:invalid_option
echo ❌ Opción no válida. Selecciona del 1 al 7.
goto pause_and_menu

:pause_and_menu
echo.
pause
cls
goto menu

:exit
echo 👋 ¡Hasta luego!
echo ===============================================
echo     🎉 Script de migraciones finalizado
echo ===============================================
pause
