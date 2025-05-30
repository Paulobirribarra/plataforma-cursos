#!/usr/bin/env python3
"""
Script de diagnóstico para verificar que la extensión problemática esté correctamente configurada
y que el sistema de control de acceso funcione correctamente.
"""

import os
import json
import sys

def check_vscode_settings():
    """Verificar configuraciones de VS Code."""
    print("🔍 Verificando configuraciones de VS Code...")
    
    # Verificar configuración del workspace
    vscode_path = "e:\\Paulo\\Github\\plataforma-cursos\\.vscode\\settings.json"
    if os.path.exists(vscode_path):
        with open(vscode_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            print(f"✅ Configuración del workspace encontrada")
            print(f"   - formatOnSave: {settings.get('editor.formatOnSave', 'No definido')}")
            print(f"   - Prettier deshabilitado para Django HTML: {settings.get('prettier.disableLanguages', [])}")
            print(f"   - Asociaciones de archivos: {settings.get('files.associations', {})}")
    else:
        print("❌ No se encontró configuración del workspace")
        return False
    
    # Verificar archivo .prettierignore
    prettierignore_path = "e:\\Paulo\\Github\\plataforma-cursos\\.prettierignore"
    if os.path.exists(prettierignore_path):
        print("✅ Archivo .prettierignore encontrado")
        with open(prettierignore_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "templates/" in content:
                print("   - Templates correctamente ignorados")
            else:
                print("   - ⚠️ Templates no están en la lista de ignorados")
    else:
        print("❌ Archivo .prettierignore no encontrado")
        return False
    
    # Verificar configuración de Prettier
    prettierrc_path = "e:\\Paulo\\Github\\plataforma-cursos\\.prettierrc.json"
    if os.path.exists(prettierrc_path):
        print("✅ Configuración de Prettier encontrada")
    else:
        print("❌ Configuración de Prettier no encontrada")
        return False
    
    return True

def check_template_integrity():
    """Verificar integridad de templates Django."""
    print("\n🔍 Verificando integridad de templates Django...")
    
    template_path = "e:\\Paulo\\Github\\plataforma-cursos\\templates\\cursos\\course_detail.html"
    
    if not os.path.exists(template_path):
        print(f"❌ Template no encontrado: {template_path}")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar etiquetas Django críticas
    critical_tags = [
        '{% extends \'base.html\' %}',
        '{% block title %}',
        '{% block content %}',
        '{% if course.resources.all %}',
        '{% if can_access_resources %}',
        '{% if request.user.is_staff %}',
        '{% endblock %}'
    ]
    
    broken_tags = []
    for tag in critical_tags:
        if tag not in content:
            broken_tags.append(tag)
    
    if broken_tags:
        print(f"❌ Etiquetas Django rotas encontradas:")
        for tag in broken_tags:
            print(f"   - {tag}")
        return False
    else:
        print("✅ Todas las etiquetas Django están correctamente formateadas")
    
    # Verificar que no hay etiquetas rotas por saltos de línea
    problematic_patterns = [
        '{% extends \'base.html\' %} {% block',
        '{%\nblock',
        '{%\nif',
        '{%\nendif',
        '{%\nfor',
        '{%\nendfor'
    ]
    
    found_problems = []
    for pattern in problematic_patterns:
        if pattern in content:
            found_problems.append(pattern)
    
    if found_problems:
        print(f"⚠️ Patrones problemáticos encontrados:")
        for pattern in found_problems:
            print(f"   - {repr(pattern)}")
        return False
    else:
        print("✅ No se encontraron patrones problemáticos")
    
    return True

def main():
    """Función principal."""
    print("🚀 Diagnóstico del Sistema de Control de Acceso y Configuración VS Code")
    print("=" * 70)
    
    # Verificar configuraciones
    vscode_ok = check_vscode_settings()
    template_ok = check_template_integrity()
    
    print("\n" + "=" * 70)
    print("📋 RESUMEN:")
    
    if vscode_ok and template_ok:
        print("✅ Todo está funcionando correctamente!")
        print("\n📌 PRÓXIMOS PASOS:")
        print("1. Reinicia VS Code para que las nuevas configuraciones tomen efecto")
        print("2. Abre el archivo course_detail.html y verifica que no se reformatee automáticamente")
        print("3. Si aún hay problemas, deshabilita temporalmente la extensión Prettier")
        
        # Instrucciones para deshabilitar Prettier si es necesario
        print("\n🔧 Para deshabilitar Prettier temporalmente:")
        print("   1. Ctrl+Shift+P → 'Extensions: Disable'")
        print("   2. Buscar 'Prettier - Code formatter'")
        print("   3. Clic en 'Disable (Workspace)'")
        
        return True
    else:
        print("❌ Se encontraron problemas que necesitan ser resueltos")
        
        if not vscode_ok:
            print("\n🔧 SOLUCIONES para VS Code:")
            print("- Verificar que los archivos de configuración estén presentes")
            print("- Reiniciar VS Code")
            
        if not template_ok:
            print("\n🔧 SOLUCIONES para templates:")
            print("- El archivo course_detail.html necesita ser corregido manualmente")
            print("- Verificar que no haya extensiones formateando automáticamente")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
