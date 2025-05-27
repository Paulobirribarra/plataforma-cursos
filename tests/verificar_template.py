#!/usr/bin/env python
"""
Script para verificar qué archivo de template está usando la vista purchase_success.
"""
import os
import sys

# Configurar acceso al proyecto desde la carpeta tests
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Verificar si la vista está usando la plantilla correcta
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = os.path.join(base_dir, 'templates', 'pagos')
view_file = os.path.join(base_dir, 'pagos', 'views.py')

def check_template():
    print("Verificando qué plantilla está usando la vista purchase_success...")
    
    # Leer el archivo de vistas
    with open(view_file, 'r', encoding='utf-8') as f:
        view_content = f.read()
    
    # Buscar la referencia a la plantilla
    if "render(request, 'pagos/purchase_success_fixed.html'" in view_content:
        print("✅ La vista está usando la plantilla corregida (purchase_success_fixed.html)")
        return True
    elif "render(request, 'pagos/purchase_success.html'" in view_content:
        print("❌ La vista está usando la plantilla original (purchase_success.html)")
        
        # Verificar si el archivo fixed existe
        fixed_template = os.path.join(template_dir, 'purchase_success_fixed.html')
        if os.path.exists(fixed_template):
            print("✅ El archivo purchase_success_fixed.html existe en el directorio de templates")
            print("❗ Deberías cambiar la vista para usar purchase_success_fixed.html")
        else:
            print("❌ El archivo purchase_success_fixed.html no existe en el directorio de templates")
            
        return False
    else:
        print("❓ No se pudo determinar qué plantilla está usando la vista")
        return False

if __name__ == "__main__":
    print("="*60)
    print(" VERIFICACIÓN DE PLANTILLA USADA EN PURCHASE_SUCCESS ")
    print("="*60)
    
    if check_template():
        print("\n✅ La vista está usando la plantilla corregida!")
    else:
        print("\n❌ La vista no está usando la plantilla corregida. Verifica el archivo de vistas.")
        sys.exit(1)
