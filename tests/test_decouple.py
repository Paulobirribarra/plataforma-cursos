#!/usr/bin/env python
"""
Script para diagnosticar la configuración de decouple.
"""
import os
import sys

print("🔍 DIAGNÓSTICO DE CONFIGURACIÓN...")
print(f"📁 Directorio actual: {os.getcwd()}")
print(f"🐍 Python executable: {sys.executable}")

# Verificar si el archivo .env existe
env_file = ".env"
if os.path.exists(env_file):
    print(f"✅ Archivo .env encontrado en: {os.path.abspath(env_file)}")
    
    with open(env_file, 'r') as f:
        content = f.read()
        
    # Buscar la línea de WEBPAY_API_KEY
    for line in content.split('\n'):
        if 'WEBPAY_API_KEY' in line:
            print(f"🔑 En archivo: {line}")
            
else:
    print(f"❌ Archivo .env NO encontrado")

# Probar decouple
try:
    from decouple import config
    api_key = config("WEBPAY_API_KEY")
    print(f"🔧 Decouple lee: WEBPAY_API_KEY={api_key}")
except Exception as e:
    print(f"❌ Error con decouple: {e}")

# Verificar variables de entorno del sistema
webpay_api_key_env = os.environ.get('WEBPAY_API_KEY')
if webpay_api_key_env:
    print(f"🌍 Variable de entorno: WEBPAY_API_KEY={webpay_api_key_env}")
else:
    print("⚠️  Variable WEBPAY_API_KEY no encontrada en entorno")

# Verificar si hay archivos .env en directorios padre
parent_dirs = []
current_dir = os.path.abspath('.')
for i in range(3):  # Buscar hasta 3 niveles arriba
    current_dir = os.path.dirname(current_dir)
    env_path = os.path.join(current_dir, '.env')
    if os.path.exists(env_path):
        parent_dirs.append(env_path)

if parent_dirs:
    print(f"📂 Archivos .env en directorios padre: {parent_dirs}")
