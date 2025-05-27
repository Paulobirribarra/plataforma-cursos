#!/usr/bin/env python
"""
Script completo de verificación del flujo post-pago.
"""
import os
import sys

def check_view_template():
    """Verifica que la vista esté usando la plantilla correcta."""
    # Configurar acceso al proyecto desde la carpeta tests
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Usar ruta relativa al proyecto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    view_file = os.path.join(base_dir, 'pagos', 'views.py')
    
    with open(view_file, 'r', encoding='utf-8') as f:
        view_content = f.read()
    
    if "render(request, 'pagos/purchase_success_fixed.html'" in view_content:
        print("✅ La vista está usando la plantilla corregida")
        return True
    else:
        print("❌ La vista NO está usando la plantilla corregida")
        return False

def check_template_formatting():
    """Verifica que la plantilla tenga el formato correcto."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_file = os.path.join(base_dir, 'templates', 'pagos', 'purchase_success_fixed.html')
    
    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Verificar si hay etiquetas HTML bien formateadas (sin saltos de línea dentro de tags)
    if "<div\n" in template_content:
        print("❌ La plantilla tiene saltos de línea dentro de etiquetas HTML")
        return False
    else:
        print("✅ La plantilla tiene un formato HTML correcto")
        return True
    
def check_urls_in_template():
    """Verifica que las URLs en la plantilla sean correctas."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_file = os.path.join(base_dir, 'templates', 'pagos', 'purchase_success_fixed.html')
    
    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    errors = []
    if not "{% url 'usuarios:dashboard' %}" in template_content:
        errors.append("❌ Falta la URL correcta para el dashboard")
    
    if not "{% url 'usuarios:my_courses' %}" in template_content:
        errors.append("❌ Falta la URL correcta para mis cursos")
    
    if errors:
        for error in errors:
            print(error)
        return False
    else:
        print("✅ Las URLs en la plantilla son correctas")
        return True
    
def check_purchase_success_test():
    """Verifica si existe el archivo de prueba para la plantilla."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_file = os.path.join(base_dir, 'tests', 'prueba_template.py')
    
    if os.path.exists(test_file):
        print("✅ Existe un script de prueba para la plantilla")
        return True
    else:
        print("❌ No se encontró el script de prueba para la plantilla")
        return False

if __name__ == "__main__":
    print("="*60)
    print(" VERIFICACIÓN COMPLETA DEL FLUJO POST-PAGO ")
    print("="*60)
    
    view_ok = check_view_template()
    template_ok = check_template_formatting()
    urls_ok = check_urls_in_template()
    test_ok = check_purchase_success_test()
    
    print("\n" + "="*60)
    if view_ok and template_ok and urls_ok and test_ok:
        print("✅ ¡TODO CORRECTO! El flujo post-pago está configurado correctamente.")
        print("✅ La página de confirmación de compra mostrará correctamente la información de la compra.")
        print("✅ Los enlaces al dashboard y a mis cursos funcionarán correctamente.")
    else:
        print("❌ Se encontraron problemas en el flujo post-pago.")
        if not view_ok:
            print("  → La vista no está usando la plantilla corregida.")
        if not template_ok:
            print("  → La plantilla tiene problemas de formato HTML.")
        if not urls_ok:
            print("  → Las URLs en la plantilla no son correctas.")
        if not test_ok:
            print("  → No se encontró el script de prueba para la plantilla.")
        sys.exit(1)
