"""
Configuración para que los tests puedan acceder a los módulos del proyecto.
"""
import os
import sys
import django

# Asegurarse de que el directorio padre esté en el PATH
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Configurar Django para usar las configuraciones del proyecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plataforma_cursos.settings')
django.setup()
