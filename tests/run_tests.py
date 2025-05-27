#!/usr/bin/env python
"""
Script principal para ejecutar todas las pruebas del sistema.
"""
import os
import sys
import subprocess

# Importar configuración de inicialización
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)

# Intentar importar termcolor, o crear una función de reemplazo
try:
    from termcolor import colored
except ImportError:
    # Si termcolor no está instalado, crear una función similar pero sin color
    def colored(text, color=None, on_color=None, attrs=None):
        """Versión simple de colored sin colores"""
        return text

def run_test(test_file):
    """Ejecuta un archivo de prueba individual."""
    print(colored(f"\n{'='*60}", "cyan"))
    print(colored(f" EJECUTANDO PRUEBA: {test_file} ", "cyan", attrs=["bold"]))
    print(colored(f"{'='*60}", "cyan"))
    
    # Ejecutar como un módulo Python
    module_name = f"tests.{os.path.splitext(test_file)[0]}"
    result = subprocess.run([sys.executable, "-m", module_name], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print(colored(f"✅ {test_file}: PRUEBA EXITOSA", "green", attrs=["bold"]))
        print(colored(result.stdout, "green"))
        return True
    else:
        print(colored(f"❌ {test_file}: PRUEBA FALLIDA", "red", attrs=["bold"]))
        print(colored(result.stdout, "yellow"))
        print(colored(result.stderr, "red"))
        return False

def run_all_tests():
    """Ejecuta todas las pruebas disponibles."""
    print(colored("\n🧪 INICIANDO EJECUCIÓN DE TODAS LAS PRUEBAS", "blue", attrs=["bold"]))
    
    # Lista de pruebas a ejecutar en orden
    test_files = [
        "test_urls.py",
        "verificar_template.py"
    ]
    
    results = []
    for test_file in test_files:
        results.append((test_file, run_test(test_file)))
    
    # Mostrar resumen
    print(colored("\n\n📊 RESUMEN DE PRUEBAS:", "blue", attrs=["bold"]))
    
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    
    for test_file, success in results:
        status = colored("✅ PASÓ", "green", attrs=["bold"]) if success else colored("❌ FALLÓ", "red", attrs=["bold"])
        print(f"{test_file}: {status}")
    
    print(colored(f"\nRESULTADO FINAL: {passed} pruebas exitosas, {failed} pruebas fallidas", 
                "green" if failed == 0 else "red", attrs=["bold"]))
    
    return failed == 0

if __name__ == "__main__":
    # Tratar de instalar termcolor si no está disponible
    try:
        import termcolor
    except ImportError:
        try:
            print("Instalando dependencias necesarias (termcolor)...")
            subprocess.run([sys.executable, "-m", "pip", "install", "termcolor"], check=True)
            from termcolor import colored
            print(colored("✅ termcolor instalado correctamente", "green"))
        except Exception:
            print("No se pudo instalar termcolor, continuando sin colores...")
    
    if run_all_tests():
        print(colored("\n✅ Todas las pruebas pasaron exitosamente!", "green", attrs=["bold"]))
        sys.exit(0)
    else:
        print(colored("\n❌ Una o más pruebas fallaron. Revisa los errores arriba.", "red", attrs=["bold"]))
        sys.exit(1)
