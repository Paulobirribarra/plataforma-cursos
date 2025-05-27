# Datos de Prueba para Webpay

Este documento contiene los datos de tarjeta de prueba para realizar pagos en el ambiente de integración de Webpay.

## Configuración del Ambiente de Integración

Para configurar el ambiente de integración de Webpay, necesitas agregar las siguientes variables en tu archivo `.env`:

```
# Configuración de Webpay (Transbank) - Ambiente de Integración
WEBPAY_BASE_URL=https://webpay3gint.transbank.cl/rswebpaytransaction/api/webpay/v1.2
WEBPAY_COMMERCE_CODE=597055555532
WEBPAY_API_KEY=579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C
```

Nota: Estas son credenciales públicas proporcionadas por Transbank para pruebas en su ambiente de integración y pueden ser utilizadas por cualquier desarrollador.

## Tarjeta de Crédito para Ambiente de Pruebas

Utiliza los siguientes datos para realizar pruebas de pago:

- **Número de tarjeta**: 4051 8856 0044 6623
- **Fecha de expiración**: Cualquier fecha futura (ejemplo: 12/25)
- **CVV**: 123
- **RUT**: 11.111.111-1
- **Contraseña**: 123

## Instrucciones de Uso

1. Al realizar una compra en la plataforma, serás redirigido al formulario de pago de Webpay
2. Ingresa los datos de prueba mencionados arriba
3. El pago debería ser aprobado y serás redirigido a la página de confirmación

## Consideraciones

- Estos datos solo funcionan en el ambiente de integración/pruebas
- Para el ambiente de producción debes utilizar tarjetas reales
- En caso de error, verifica los logs en la consola de administración de Webpay

## Resultados Esperados

Al utilizar estos datos de prueba, la transacción debería ser aprobada y se debe mostrar la página de compra exitosa con el resumen de la transacción.
