# Datos de Prueba para Webpay - SDK Transbank v6.0.0

Este documento contiene los datos de tarjeta de prueba para realizar pagos en el ambiente de integración de Webpay usando el **SDK oficial de Transbank v6.0.0**.

## ⚙️ Configuración del Ambiente de Integración

### Instalación del SDK
```bash
pip install transbank-sdk==6.0.0
```

### Variables de Ambiente (.env)
```env
# Configuración de Webpay (Transbank) - Ambiente de Integración
WEBPAY_ENVIRONMENT=INTEGRATION
# Las credenciales se configuran automáticamente del SDK para integración
```

### Credenciales Oficiales de Integración
El SDK v6.0.0 utiliza automáticamente estas credenciales para el ambiente de integración:

- **Commerce Code**: `597055555532`
- **API Key**: `579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C`
- **URL Base**: `https://webpay3gint.transbank.cl`
- **Integration Type**: `TEST`

**Nota**: Estas son credenciales públicas proporcionadas por Transbank para pruebas en su ambiente de integración y pueden ser utilizadas por cualquier desarrollador.

## 💳 Tarjeta de Crédito para Ambiente de Pruebas

Utiliza los siguientes datos para realizar pruebas de pago:

- **Número de tarjeta**: `4051 8856 0044 6623`
- **Fecha de expiración**: Cualquier fecha futura (ejemplo: `12/25`)
- **CVV**: `123`
- **RUT**: `11.111.111-1`
- **Contraseña**: `123`

## 🔧 Implementación con SDK v6.0.0

### Código de Ejemplo
```python
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType
from transbank.common.options import WebpayOptions

# Configuración para integración
options = WebpayOptions(
    commerce_code='597055555532',
    api_key='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C',
    integration_type=IntegrationType.TEST
)

# Crear transacción
tx = Transaction(options)
response = tx.create(
    buy_order="orden_123",
    session_id="sesion_456",
    amount=10000,  # $10.000 CLP
    return_url="http://localhost:8000/pagos/confirmacion/"
)

# El response contiene:
# - token: Token único de la transacción
# - url: URL del formulario de Webpay
```

## 📋 Instrucciones de Uso

1. **Configurar el proyecto** con el SDK v6.0.0
2. Al realizar una compra en la plataforma, serás redirigido al formulario de pago de Webpay
3. Ingresa los datos de prueba mencionados arriba
4. El pago debería ser aprobado y serás redirigido a la página de confirmación

## ⚠️ Consideraciones Importantes

- Estos datos solo funcionan en el ambiente de integración/pruebas
- Para el ambiente de producción debes utilizar tarjetas reales
- El SDK v6.0.0 maneja automáticamente la autenticación y headers
- En caso de error, verificar logs con `logger.info()` habilitado

## 🧪 Testing y Verificación

### Script de Prueba Rápida
```python
# tests/test_webpay_sdk.py - incluido en el proyecto
python tests/test_webpay_sdk.py
```

### Resultado Esperado
```
🚀 Iniciando prueba de Webpay con SDK oficial...
✅ Webpay configurado correctamente
✅ Transacción creada exitosamente:
   Token: 01ab25abb1c5466b76b003...
   URL: https://webpay3gint.transbank.cl/webpayserver/initTransaction
🎉 ¡Todas las pruebas pasaron exitosamente!
```

## 🚨 Solución de Problemas Comunes

### Error: "cannot import name 'WebpayPlus'"
**Solución**: Usar la importación correcta para v6.0.0
```python
# ✅ Correcto
from transbank.webpay.webpay_plus.transaction import Transaction
```

### Error: 401 Unauthorized
**Causas posibles**:
- Credenciales incorrectas para el ambiente
- `integration_type` mal configurado
- SDK no actualizado

**Solución**: Verificar configuración con `WebpayOptions`

## 📊 Resultados Esperados

Al utilizar estos datos de prueba con el SDK v6.0.0:
- ✅ La transacción debería ser aprobada
- ✅ Se debe mostrar la página de compra exitosa
- ✅ Los logs deben mostrar "Transacción confirmada exitosamente"
- ✅ El estado del pago debe cambiar a "completed"

## 🔗 Referencias

- **SDK Oficial**: https://github.com/TransbankDevelopers/transbank-sdk-python
- **Documentación Transbank**: https://www.transbankdevelopers.cl/
- **Ambiente de Integración**: https://webpay3gint.transbank.cl
