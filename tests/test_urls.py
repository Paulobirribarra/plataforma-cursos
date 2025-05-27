#!/usr/bin/env python
"""
Script simple para probar la página de éxito de compra.
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plataforma_cursos.settings')
django.setup()

from django.urls import reverse

def test_urls():
    """Probar que las URLs estén configuradas correctamente."""
    print("\n🔗 Probando configuración de URLs...")
    
    urls_to_test = [
        ('usuarios:dashboard', {}),
        ('usuarios:my_courses', {}),
        ('pagos:purchase_success', {}),
        ('membresias:plan_list', {}),
        ('carrito:cart_detail', {}),
    ]
    
    all_ok = True
    for url_name, kwargs in urls_to_test:
        try:
            url = reverse(url_name, kwargs=kwargs)
            print(f"✅ {url_name}: {url}")
        except Exception as e:
            print(f"❌ {url_name}: Error - {e}")
            all_ok = False
    
    return all_ok

if __name__ == "__main__":
    if test_urls():
        print("✅ Todas las URLs están configuradas correctamente")
    else:
        print("❌ Hay problemas con algunas URLs")
        sys.exit(1)
