# Plataforma de Cursos - Asesorias Futuro LTD

Bienvenido(a) al proyecto **Plataforma de Cursos**, una aplicación web para gestionar y mostrar cursos en línea, construida con Django y PostgreSQL.

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
    ```
    venv\Scripts\activate
    ```
3. ***Instala las dependencias***:
    ```
    pip install -r requirements.txt
    ```
4. ***Configura las variables de entorno***.
    Crea el archivo .env:
    ```
    SECRET_KEY=tu_clave_secreta_aqui
    DEBUG=True
    DATABASE_URL=postgresql://postgres:tu_contraseña@localhost:5432/plataforma_cursos
    DATABASE_PASSWORD=tu_contraseña
    EMAIL_HOST_USER=tu_email@gmail.com
    EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicación
    ```
5. ***Configura PostgreSQL***:
    ```
    CREATE USER postgres WITH PASSWORD 'tu_contraseña';
    CREATE DATABASE plataforma_cursos OWNER postgres;
    ```
6. ***Aplica las migraciones o reinicia la base de datos***:
    Opción 1: Migraciones normales:

    ```
    python manage.py makemigrations
    python manage.py migrate
    ```
    Opción 2: Usa el script de reinicio (Windows PowerShell):
    ```
    .\reset_database.ps1
    ```
    Esto elimina y recrea la base de datos, reinicia migraciones, y crea un superusuario (admin, admin@example.com, admin12345).
7. ***Crea un superusuario manualmente (opcional)***:
    ```
    python manage.py createsuperuser
    ```
8. ***Inicia el servidor***:
    ```
    python manage.py runserver
    ```

    Abre tu navegador en http://127.0.0.1:8000/ para ver la aplicación.

**Estructura del Proyecto**
- cursos/: Aplicación principal para gestionar cursos.
- usuarios/: Aplicación para manejar usuarios.
- templates/: Plantillas HTML (base.html, home.html, etc.).
- static/: Archivos estáticos (imágenes, CSS, JS).
- media/: Archivos multimedia subidos por usuarios.

**Script de Reinicio (reset_database.ps1)**

Este script reinicia la base de datos PostgreSQL y las migraciones. Úsalo con precaución, ya que elimina todos los datos existentes. Revisa el contenido antes de ejecutarlo:
- Requiere PowerShell.
- Configura la variable PGPASSWORD con tu contraseña de PostgreSQL.