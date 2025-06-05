# Plataforma de Cursos - Asesorias Futuro LTD

Proyecto **Plataforma de Cursos**, una aplicación web para gestionar y mostrar cursos en línea, construida con Django y PostgreSQL.

## Requisitos Previos

- Python 3.11 o superior
- Git
- PostgreSQL instalado y configurado (con un usuario `postgres` y base de datos `plataforma_cursos`)
- Un entorno virtual (recomendado)
- PowerShell (para el script de reinicio en Windows)

## Dependencias Principales

El proyecto utiliza las siguientes dependencias clave:

### Framework y Base de Datos
- **Django 5.2.1** - Framework web principal
- **psycopg2-binary 2.9.10** - Adaptador PostgreSQL
- **python-decouple 3.8** - Manejo de variables de entorno

### Sistema de Pagos
- **transbank-sdk 6.0.0** - SDK oficial de Transbank para Webpay
- **requests 2.28.2** - Cliente HTTP para APIs

### UI y Templates
- **django-widget-tweaks 1.5.0** - Personalización de formularios
- **django-allauth 65.8.0** - Sistema de autenticación avanzado
- **pillow 11.2.1** - Procesamiento de imágenes

### Otras Dependencias
Ver archivo `requirements.txt` para la lista completa.

## Instalación

1. **Clona el repositorio**:

   ```bash
   git clone https://github.com/Paulobirribarra/plataforma-cursos.git
   cd plataforma-cursos
   ```

2. **Crea y activa un entorno virtual**:

   ```powershell
   python -m venv env
   .\env\Scripts\Activate.ps1
   ```

3. **Instala las dependencias**:

   ```powershell
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno**:
   Copia el archivo `.env.example` a `.env` y configura tus valores:

   ```powershell
   Copy-Item .env.example .env
   ```

   Edita el archivo `.env` con tus datos reales:

   ```env
   SECRET_KEY=tu_clave_secreta_super_segura_aqui
   DEBUG=True
   DATABASE_URL=postgresql://postgres:tu_contraseña@localhost:5432/plataforma_cursos
   DATABASE_PASSWORD=tu_contraseña
   EMAIL_HOST_USER=tu_email@gmail.com
   EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicación
   
   # Configuración de Webpay (Transbank) - SDK v6.0.0
   WEBPAY_ENVIRONMENT=INTEGRATION  # Para desarrollo, PRODUCTION para producción
   # Para ambiente de integración, las credenciales se configuran automáticamente
   # Para producción, descomentar y configurar:
   # WEBPAY_COMMERCE_CODE=tu_codigo_de_comercio_aqui
   # WEBPAY_API_KEY=tu_api_key_aqui
   ```

5. **Configura PostgreSQL**:
   ```sql
   CREATE USER postgres WITH PASSWORD 'tu_contraseña';
   CREATE DATABASE plataforma_cursos OWNER postgres;
   ```

## Configuración de Base de Datos y Migraciones

### Opción 1: Migraciones Manuales (Recomendado para desarrollo)

Para un mayor control sobre el proceso, ejecuta las migraciones manualmente en este orden:

```powershell
# 1. Eliminar migraciones existentes (si las hay)
Remove-Item usuarios\migrations\0*.py -ErrorAction SilentlyContinue
Remove-Item cursos\migrations\0*.py -ErrorAction SilentlyContinue
Remove-Item pagos\migrations\0*.py -ErrorAction SilentlyContinue
Remove-Item membresias\migrations\0*.py -ErrorAction SilentlyContinue
Remove-Item carrito\migrations\0*.py -ErrorAction SilentlyContinue

# 2. Generar migraciones en orden específico (respetando dependencias)
python manage.py makemigrations usuarios      # Primero los usuarios
python manage.py makemigrations membresias    # Luego membresías (depende de usuarios)
python manage.py makemigrations cursos        # Cursos (depende de usuarios y membresías)
python manage.py makemigrations pagos         # Pagos (depende de usuarios)
python manage.py makemigrations carrito       # Carrito (depende de usuarios y cursos)

# 3. Aplicar todas las migraciones
python manage.py migrate

# 4. Crear superusuario
python manage.py createsuperuser --email admin@plataforma-cursos.local
```

### Opción 2: Script Automatizado (Solo para reinicio completo)

**⚠️ ADVERTENCIA: Este script elimina TODOS los datos existentes**

```powershell
.\reset_database.ps1
```

**¿Cuándo usar cada opción?**

- **Migraciones manuales**: Para desarrollo normal, cambios incrementales
- **Script automatizado**: Solo para reiniciar completamente el proyecto o resolver problemas complejos de migración

### Opción 3: Inicialización desde cero

Si es la primera vez que configuras el proyecto:

```powershell
# 1. Crear y configurar la base de datos
psql -U postgres -c "DROP DATABASE IF EXISTS plataforma_cursos;"
psql -U postgres -c "CREATE DATABASE plataforma_cursos;"

# 2. Ejecutar migraciones en orden
python manage.py migrate                      # Migraciones de Django primero
python manage.py makemigrations usuarios
python manage.py migrate usuarios
python manage.py makemigrations membresias
python manage.py migrate membresias
python manage.py makemigrations cursos
python manage.py migrate cursos
python manage.py makemigrations pagos
python manage.py migrate pagos
python manage.py makemigrations carrito
python manage.py migrate carrito

# 3. Crear superusuario
python manage.py createsuperuser --email admin@plataforma-cursos.local
```

## Inicio del Servidor

```powershell
python manage.py runserver
```

Abre tu navegador en http://127.0.0.1:8000/ para ver la aplicación.

## Acceso al Panel de Administración

- URL: http://127.0.0.1:8000/admin/
- Email: admin@plataforma-cursos.local (o el que hayas configurado)
- Password: El que definiste al crear el superusuario

**Estructura del Proyecto**

- cursos/: Aplicación principal para gestionar cursos.
- usuarios/: Aplicación para manejar usuarios customizados.
- pagos/: Aplicación para procesar pagos con Webpay (SDK v6.0.0).
- membresias/: Aplicación para gestionar planes de membresía.
- carrito/: Aplicación para el carrito de compras.
- templates/: Plantillas HTML (base.html, home.html, etc.).
- static/: Archivos estáticos (imágenes, CSS, JS).
- media/: Archivos multimedia subidos por usuarios.
- documentacion/: Guías técnicas y de implementación.
- tests/: Scripts de testing y validación.

## Funcionalidades Principales

### 💳 Sistema de Pagos (Webpay)
- **SDK oficial Transbank v6.0.0** integrado
- **Ambiente de integración** configurado automáticamente
- **Testing automatizado** de transacciones
- **Manejo de errores** robusto
- **Logging detallado** para debugging

### 🎓 Gestión de Cursos
- **Cursos premium y gratuitos**
- **Cursos de recompensa** por membresías
- **Administración avanzada** con interfaz moderna
- **Categorización** y filtrado

### 👥 Sistema de Membresías
- **Planes de membresía** con diferentes beneficios
- **Acceso a cursos exclusivos**
- **Gestión automática** de estados

### 🛒 Carrito de Compras
- **Compras múltiples** (cursos + membresías)
- **Pagos mixtos** (gratuitos y pagados)
- **Procesamiento automático** post-pago

### 🔐 Seguridad Avanzada
- **Usuario personalizado** con campos de seguridad
- **Bloqueo automático** de cuentas
- **Verificación de email**
- **Seguimiento de IPs**

## Seguridad del Modelo de Usuario

El proyecto utiliza un modelo de usuario personalizado (`CustomUser`) que mejora la seguridad con:

### Características de Seguridad Implementadas:

- **Email como identificador único**: Más seguro que username
- **Campos adicionales de seguridad**:
  - `failed_login_attempts`: Contador de intentos fallidos
  - `account_locked_until`: Bloqueo temporal de cuenta
  - `last_login_ip`: Seguimiento de direcciones IP
  - `is_email_verified`: Verificación de email obligatoria
  - `email_verification_token`: Token para verificación

### Recomendaciones de Seguridad:

1. **Contraseñas fuertes**: Usar contraseñas con al menos 12 caracteres, mayúsculas, minúsculas, números y símbolos
2. **Verificación de email**: Activar verificación de email en producción
3. **Bloqueo de cuenta**: El sistema bloquea automáticamente cuentas después de 5 intentos fallidos
4. **Variables de entorno**: Nunca subir archivos `.env` al repositorio
5. **HTTPS en producción**: Configurar SSL/TLS para el servidor de producción

### Script de Reinicio (reset_database.ps1)

**⚠️ ADVERTENCIA: Este script elimina TODOS los datos existentes**

Características del script:

- Reinicia completamente la base de datos PostgreSQL
- Elimina y recrea todas las migraciones
- Crea un superusuario con credenciales seguras
- Maneja el orden correcto de dependencias entre aplicaciones

**Credenciales del superusuario creado por el script**:

- Email: `admin@plataforma-cursos.local`
- Password: `Admin123!Dev`
- Nombre: `Administrador Sistema`

**Requisitos para ejecutar el script**:

- PowerShell (Windows)
- PostgreSQL configurado y ejecutándose
- Variables de entorno configuradas en `.env`
- Entorno virtual activado

### Solución de Problemas Comunes

**Error: "no existe la relación usuarios_customuser"**

```powershell
# Ejecutar migraciones en orden específico
python manage.py migrate contenttypes
python manage.py migrate auth
python manage.py makemigrations usuarios
python manage.py migrate usuarios
```

**Error: "Unable to copy venvlauncher.exe"**

```powershell
# Eliminar entorno virtual corrupto y crear uno nuevo
Remove-Item -Recurse -Force env
python -m venv env
.\env\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Error: "App isn't loaded"**

```powershell
# Verificar que todas las apps están en INSTALLED_APPS en settings.py
# Ejecutar migraciones una por una si es necesario
```

**Error: "cannot import name 'WebpayPlus'" (SDK Transbank)**

```powershell
# Verificar versión del SDK
pip show transbank-sdk

# Reinstalar si es necesario
pip uninstall transbank-sdk
pip install transbank-sdk==6.0.0
```

**Error: 401 Unauthorized en Webpay**

```powershell
# Verificar configuración de ambiente
# En .env debe estar: WEBPAY_ENVIRONMENT=INTEGRATION

# Probar configuración
python tests\test_webpay_sdk.py
```

## 🔧 Scripts de Utilidad

### Testing y Validación
```powershell
# Probar SDK de Transbank
python tests\test_webpay_sdk.py

# Ejecutar todos los tests
python tests\run_tests.py

# Diagnóstico del sistema
python tests\diagnostic_vscode_fix.py
```

### Gestión de Datos
```powershell
# Poblar datos de prueba
.\poblar_datos.ps1

# Crear sistema completo de prueba
python scripts\crear_sistema_completo.py

# Poblar solo cursos
python scripts\poblar_cursos.py
```

## Datos de Prueba para Webpay (SDK v6.0.0)

Para realizar pruebas de pago en el ambiente de integración de Webpay, utiliza los siguientes datos:

| Campo               | Valor                              |
| ------------------- | ---------------------------------- |
| Número de tarjeta   | 4051 8856 0044 6623                |
| Fecha de expiración | Cualquier fecha futura (ej: 12/25) |
| CVV                 | 123                                |
| RUT                 | 11.111.111-1                       |
| Contraseña          | 123                                |

### 🚀 SDK de Transbank v6.0.0

El proyecto utiliza el **SDK oficial de Transbank v6.0.0** para la integración con Webpay:

- **Configuración automática** para ambiente de integración
- **Credenciales oficiales** incluidas para desarrollo
- **Manejo automático** de headers y autenticación
- **Testing integrado** con scripts de validación

### 📋 Verificación Rápida de Webpay

```powershell
# Probar configuración de Webpay
python tests\test_webpay_sdk.py
```

**Resultado esperado:**
```
✅ Webpay configurado correctamente
✅ Transacción creada exitosamente
🎉 ¡Todas las pruebas pasaron exitosamente!
```

## 📚 Documentación Detallada

### Guías de Implementación
- **[Solución Completa de Pagos](documentacion/SOLUCION_COMPLETA_PAGOS.md)** - Arquitectura y implementación completa
- **[Guía Rápida SDK Transbank](documentacion/GUIA_RAPIDA_SDK_TRANSBANK.md)** - Instalación y configuración en 5 minutos
- **[Datos de Prueba Webpay](documentacion/DATOS_PRUEBA_WEBPAY.md)** - Credenciales y datos de testing
- **[Notas Técnicas de Migración](documentacion/NOTAS_TECNICAS_MIGRACION_SDK.md)** - Detalles técnicos de la implementación

### Testing y Verificación
- **[Prueba de Flujo de Compra](documentacion/PRUEBA_FLUJO_COMPRA.md)** - Testing completo del sistema
- **Script de testing**: `tests/test_webpay_sdk.py`

**Importante**: El sistema utiliza el SDK oficial de Transbank v6.0.0. Para configuración de desarrollo, solo necesitas establecer `WEBPAY_ENVIRONMENT=INTEGRATION` en tu archivo `.env`. Las credenciales de integración se configuran automáticamente.
