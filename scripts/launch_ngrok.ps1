#!/usr/bin/env pwsh

# Script para lanzar ngrok
Write-Host "🚀 Lanzando ngrok para exponer la aplicación..." -ForegroundColor Green

# Verificar que el servidor Django esté corriendo
$django_running = Get-Process | Where-Object {$_.ProcessName -eq "python" -and $_.CommandLine -like "*manage.py*runserver*"}

if (-not $django_running) {
    Write-Host "⚠️  El servidor Django no está ejecutándose. Iniciándolo..." -ForegroundColor Yellow
    Start-Process -NoNewWindow python -ArgumentList "manage.py", "runserver", "0.0.0.0:8000"
    Start-Sleep -Seconds 3
}

# Lanzar ngrok
Write-Host "🌐 Iniciando túnel ngrok..." -ForegroundColor Cyan
try {
    # Intentar con la nueva sintaxis de ngrok
    ngrok http --log=stdout 8000
} catch {
    Write-Host "❌ Error al lanzar ngrok: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 Asegúrate de que ngrok esté configurado correctamente" -ForegroundColor Yellow
}
