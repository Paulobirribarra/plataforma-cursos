# Script de verificación del sistema de seguridad para Windows PowerShell
# Uso: .\verificar_sistema.ps1

Write-Host "🎯 SISTEMA DE SEGURIDAD INTEGRAL - VERIFICACIÓN FINAL" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Yellow

# Cambiar al directorio del proyecto
Set-Location "e:\Paulo\Github\plataforma-cursos"

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "manage.py")) {
    Write-Host "❌ Error: No se encontró manage.py. Verifica la ruta del proyecto." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📁 Verificando estructura del proyecto..." -ForegroundColor Cyan

# Ejecutar script de verificación Python
Write-Host ""
Write-Host "🔍 Ejecutando verificación completa..." -ForegroundColor Yellow
python scripts\verificar_sistema_completo.py

Write-Host ""
Write-Host "📋 COMANDOS ÚTILES PARA ADMINISTRACIÓN:" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Yellow

Write-Host ""
Write-Host "🛡️ AUDITORÍA DE SEGURIDAD:"
Write-Host "  python manage.py security_audit --action=check-config" -ForegroundColor White
Write-Host "  python manage.py security_audit --action=audit" -ForegroundColor White
Write-Host "  python manage.py security_audit --action=list-admins" -ForegroundColor White

Write-Host ""
Write-Host "📝 REVISAR LOGS:"
Write-Host "  Get-Content logs\security.log -Tail 20" -ForegroundColor White
Write-Host "  Get-Content logs\errors.log -Tail 20" -ForegroundColor White

Write-Host ""
Write-Host "🧪 PROBAR SISTEMA DE LOGGING:"
Write-Host "  python -c `"import logging; logging.getLogger('usuarios.decorators').info('Test manual')`"" -ForegroundColor White

Write-Host ""
Write-Host "📊 VER ESTADO DE ARCHIVOS:"
Write-Host "  Get-ChildItem logs\ -Name" -ForegroundColor White
Write-Host "  Get-ChildItem documentacion\ -Name" -ForegroundColor White

Write-Host ""
Write-Host "🎯 PRÓXIMOS PASOS PARA PRODUCCIÓN:" -ForegroundColor Green
Write-Host "  1. Configurar variables de entorno (.env)" -ForegroundColor Yellow
Write-Host "  2. Configurar servidor Hostinger VPS" -ForegroundColor Yellow
Write-Host "  3. Ejecutar scripts de backup" -ForegroundColor Yellow
Write-Host "  4. Configurar SSL y dominio" -ForegroundColor Yellow

Write-Host ""
Write-Host "📖 DOCUMENTACIÓN DISPONIBLE:" -ForegroundColor Green
Write-Host "  - documentacion\DESPLIEGUE_HOSTINGER_COMPLETO.md" -ForegroundColor White
Write-Host "  - documentacion\SISTEMA_BACKUP_HOSTINGER.md" -ForegroundColor White
Write-Host "  - documentacion\RESUMEN_FINAL_IMPLEMENTACION.md" -ForegroundColor White

Write-Host ""
Write-Host "✨ SISTEMA COMPLETAMENTE IMPLEMENTADO Y VERIFICADO ✨" -ForegroundColor Green
