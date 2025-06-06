@echo off
:: ================================
:: SISTEMA MAESTRO DE POBLADO DE DATOS - Windows CMD
:: ================================
echo.
echo ===============================================
echo 🎭 SISTEMA MAESTRO DE POBLADO DE DATOS 🎭
echo Plataforma Cursos - Version CMD
echo ===============================================
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado. Instala Python y agregalo al PATH.
    pause
    exit /b 1
)

:: Verificar Django
python manage.py check --deploy >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Django con advertencias pero funcional
) else (
    echo ✅ Django configurado correctamente
)

:MENU
echo.
echo 🎯 OPCIONES DISPONIBLES:
echo.
echo 1. 🎉 Poblado Completo
echo 2. 💎 Solo Membresías  
echo 3. 📚 Solo Cursos
echo 4. 📋 Solo Tipos de Consulta
echo 5. 🆓 Solo Cursos Gratuitos
echo 6. 🧹 Limpiar Todos los Datos
echo 7. 📊 Estado Actual
echo 8. 🚪 Salir
echo.

set /p choice="Selecciona una opción (1-8): "

if "%choice%"=="1" (
    python manage.py populate_master --action=complete
    goto POST_EXECUTION
)
if "%choice%"=="2" (
    python manage.py populate_master --action=membresias
    goto POST_EXECUTION
)
if "%choice%"=="3" (
    python manage.py populate_master --action=cursos
    goto POST_EXECUTION
)
if "%choice%"=="4" (
    python manage.py populate_master --action=tipos_consulta
    goto POST_EXECUTION
)
if "%choice%"=="5" (
    python manage.py populate_master --action=cursos_gratuitos
    goto POST_EXECUTION
)
if "%choice%"=="6" (
    echo.
    echo ⚠️  ATENCION: Esta acción eliminará TODOS los datos de poblado.
    set /p confirm="¿Estás seguro? Escribe CONFIRMAR para continuar: "
    if "%confirm%"=="CONFIRMAR" (
        python manage.py populate_master --action=clean_all
    ) else (
        echo Operación cancelada.
    )
    goto POST_EXECUTION
)
if "%choice%"=="7" (
    python manage.py populate_master --action=status
    goto POST_EXECUTION
)
if "%choice%"=="8" (
    echo ¡Hasta luego! 👋
    exit /b 0
)

echo Opción inválida. Selecciona entre 1-8.
goto MENU

:POST_EXECUTION
echo.
echo 💡 Admin Django: http://localhost:8000/admin/
echo 💡 Para crear superusuario: python manage.py createsuperuser
echo.
set /p continue="¿Deseas realizar otra acción? (s/n): "
if /i "%continue%"=="s" goto MENU

echo ¡Gracias por usar el Sistema Maestro de Poblado! 🎭
pause
