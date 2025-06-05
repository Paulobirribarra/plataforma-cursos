#!/usr/bin/env python
import os
import sys
import django

# Agregar el directorio del proyecto al path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plataforma_cursos.settings')
django.setup()

# Intentar importar
try:
    from blogs.models import BlogPost, ContactMessage
    print("✓ BlogPost importado correctamente")
    print("✓ ContactMessage importado correctamente")
    print(f"BlogPost tiene {len(BlogPost._meta.fields)} campos")
except ImportError as e:
    print(f"✗ Error de importación: {e}")
except Exception as e:
    print(f"✗ Error: {e}")
