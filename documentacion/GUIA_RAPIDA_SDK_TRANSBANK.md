# 🔧 GUÍA RÁPIDA - SDK TRANSBANK v6.0.0

## 🚀 Instalación Rápida

```bash
pip install transbank-sdk==6.0.0
```

## ⚡ Configuración Mínima

### 1. Variables de Ambiente (.env)
```env
WEBPAY_ENVIRONMENT=INTEGRATION  # Para desarrollo
```

### 2. Código Básico
```python
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType
from transbank.common.options import WebpayOptions

# Configuración para integración (desarrollo)
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

# Confirmar transacción (después del pago)
response = tx.commit(token)
```

## 📊 Datos de Prueba (Ambiente Integración)

### Tarjeta de Crédito
- **Número**: 4051 8856 0044 6623
- **Fecha**: 12/25
- **CVV**: 123
- **RUT**: 11.111.111-1
- **Contraseña**: 123

## 🔍 Troubleshooting

### Error Common: ImportError
```python
# ❌ NO usar (versiones antiguas)
from transbank.webpay.webpay_plus import WebpayPlus

# ✅ Usar (v6.0.0+)
from transbank.webpay.webpay_plus.transaction import Transaction
```

### Error: 401 Unauthorized
- Verificar que `integration_type=IntegrationType.TEST` para desarrollo
- Para producción usar `IntegrationType.LIVE` con credenciales reales

## 🧪 Test Rápido

```python
# Archivo: test_webpay_rapido.py
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType
from transbank.common.options import WebpayOptions

options = WebpayOptions(
    commerce_code='597055555532',
    api_key='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C',
    integration_type=IntegrationType.TEST
)

try:
    tx = Transaction(options)
    response = tx.create("test_123", "session_456", 1000, "http://localhost:8000/return/")
    print(f"✅ Token: {response['token']}")
    print(f"✅ URL: {response['url']}")
except Exception as e:
    print(f"❌ Error: {e}")
```

## 📋 Checklist de Implementación

- [ ] SDK v6.0.0 instalado
- [ ] Variables de ambiente configuradas
- [ ] Imports correctos en código
- [ ] Test de transacción funciona
- [ ] Logs habilitados para debugging

## 🔗 Referencias

- **Documentación Oficial**: https://github.com/TransbankDevelopers/transbank-sdk-python
- **Ambiente de Integración**: https://webpay3gint.transbank.cl
- **Soporte**: transbankdevelopers@continuum.cl
