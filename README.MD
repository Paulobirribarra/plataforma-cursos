# Plataforma de Cursos - Asesorias Futuro LTD

Proyecto **Plataforma de Cursos**, una aplicación web para gestionar y mostrar cursos en línea, construida con Django y PostgreSQL.

## Requisitos Previos

- Python 3.11 o superior
- Git
- PostgreSQL instalado y configurado (con un usuario `postgres` y base de datos `plataforma_cursos`)
- Un entorno virtual (recomendado)
- PowerShell (para el script de reinicio en Windows)

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
   EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicación   # Configuración de Webpay (Transbank)
   WEBPAY_BASE_URL=https://webpay3gint.transbank.cl/rswebpaytransaction/api/webpay/v1.2
   WEBPAY_COMMERCE_CODE=tu_codigo_de_comercio_aqui
   WEBPAY_API_KEY=tu_api_key_aqui
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
- pagos/: Aplicación para procesar pagos con Webpay.
- membresias/: Aplicación para gestionar planes de membresía.
- carrito/: Aplicación para el carrito de compras.
- templates/: Plantillas HTML (base.html, home.html, etc.).
- static/: Archivos estáticos (imágenes, CSS, JS).
- media/: Archivos multimedia subidos por usuarios.

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

## Datos de Prueba para Webpay

Para realizar pruebas de pago en el ambiente de integración de Webpay, utiliza los siguientes datos:

| Campo               | Valor                              |
| ------------------- | ---------------------------------- |
| Número de tarjeta   | 4051 8856 0044 6623                |
| Fecha de expiración | Cualquier fecha futura (ej: 12/25) |
| CVV                 | 123                                |
| RUT                 | 11.111.111-1                       |
| Contraseña          | 123                                |

Para más detalles, consulta el archivo [documentacion/DATOS_PRUEBA_WEBPAY.md](documentacion/DATOS_PRUEBA_WEBPAY.md)

**Importante**: Para configurar Webpay, necesitarás credenciales de integración que encontrarás en el archivo de documentación. Estas son credenciales públicas proporcionadas por Transbank para su ambiente de integración.
