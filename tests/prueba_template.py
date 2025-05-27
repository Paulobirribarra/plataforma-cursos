#!/usr/bin/env python
"""
Script para probar directamente la plantilla purchase_success_fixed.html
No requiere autenticación, simplemente renderiza la plantilla con datos de prueba
"""
import os
import django
import sys
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpRequest

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plataforma_cursos.settings")
django.setup()

def test_template():
    """Prueba la plantilla purchase_success_fixed.html directamente"""
    print("\n💡 Probando plantilla purchase_success_fixed.html...")
    
    # Datos de prueba
    context = {
        'payment': {
            'id': 12345,
            'amount': 59980.0
        },
        'purchased_items': [
            {
                'item_type': 'course',
                'course_title': 'Curso de Python Avanzado',
                'membership_name': None,
                'price_applied': 19990.0
            },
            {
                'item_type': 'membership',
                'course_title': None,
                'membership_name': 'Plan Premium',
                'price_applied': 39990.0
            }
        ],
        'has_new_membership': True,
        'has_new_courses': True
    }
    
    try:
        # Renderizar la plantilla
        print("⏳ Renderizando plantilla...")
        html = render_to_string('pagos/purchase_success_fixed.html', context)
        
        # Guardar el HTML para inspección
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prueba_template_output.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Plantilla renderizada correctamente y guardada en {output_path}")
        print("✅ La plantilla parece estar funcionando")
        return True
    except Exception as e:
        print(f"❌ Error al renderizar la plantilla: {e}")
        print(f"Traceback: {sys.exc_info()}")
        return False

if __name__ == "__main__":
    print("="*60)
    print(" PRUEBA DE PLANTILLA PURCHASE_SUCCESS_FIXED.HTML ")
    print("="*60)
    
    if test_template():
        print("\n✅ La plantilla se ha renderizado correctamente!")
    else:
        print("\n❌ La prueba ha fallado. Revisa los errores anteriores.")
        sys.exit(1)
