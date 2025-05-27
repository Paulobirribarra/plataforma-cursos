# Tests

Este directorio contiene pruebas y scripts de diagnóstico para el proyecto.

## Cómo ejecutar las pruebas

Puedes ejecutar todas las pruebas usando el script principal:

```bash
# Desde la carpeta raíz del proyecto
python -m tests.run_tests
```

O bien usar el script PowerShell:

```powershell
# Desde la carpeta raíz del proyecto
.\ejecutar_pruebas.ps1
```

## Principales archivos de prueba

- **test_urls.py**: Prueba la configuración de URLs del sistema
- **test_payment_success.py**: Prueba el flujo de éxito de pago
- **verificar_template.py**: Verifica que se esté usando la plantilla correcta
- **verificacion_completa.py**: Realiza una verificación completa del flujo post-pago

## Estructura de pruebas

- `__init__.py`: Configuración para todos los tests
- `run_tests.py`: Script para ejecutar todas las pruebas
- Scripts individuales para cada prueba específica
