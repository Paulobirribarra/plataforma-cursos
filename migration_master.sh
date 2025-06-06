#!/bin/bash
# ================================
# SISTEMA MAESTRO DE MIGRACIONES
# ================================
# Un script para dominarlas a todas 💍
# Autor: Paulo - Plataforma Cursos

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Función para mostrar mensajes con colores
print_step() {
    echo -e "${CYAN}⚡ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Función para mostrar el menú
show_menu() {
    echo ""
    echo -e "${CYAN}===================== OPCIONES =====================${NC}"
    echo -e "${GREEN}1. 🔄 MIGRACIÓN COMPLETA (Recomendado para cambio de PC)${NC}"
    echo -e "${BLUE}2. 📝 Solo crear migraciones (sin aplicar)${NC}"
    echo -e "${YELLOW}3. 🚀 Solo aplicar migraciones existentes${NC}"
    echo -e "${RED}4. 🧹 Limpiar todas las migraciones${NC}"
    echo -e "${PURPLE}5. 🗄️  Reset completo de base de datos + migraciones${NC}"
    echo -e "${WHITE}6. ℹ️  Ver estado actual de migraciones${NC}"
    echo -e "${CYAN}7. 🚪 Salir${NC}"
    echo -e "${CYAN}====================================================${NC}"
    echo ""
}

# Función para verificar si estamos en el directorio correcto
check_environment() {
    if [ ! -f "manage.py" ]; then
        print_error "No se encontró manage.py. Asegúrate de estar en el directorio raíz del proyecto Django."
        exit 1
    fi
    
    if ! command -v python &> /dev/null; then
        print_error "Python no encontrado. Asegúrate de tener Python instalado."
        exit 1
    fi
}

# Funciones principales
complete_migration() {
    print_step "🎯 Ejecutando migración completa..."
    python manage.py migrate_master --action=complete
}

create_migrations() {
    print_step "📝 Creando migraciones..."
    python manage.py migrate_master --action=create
}

apply_migrations() {
    print_step "🚀 Aplicando migraciones..."
    python manage.py migrate_master --action=apply
}

clean_migrations() {
    read -p "⚠️  ¿Estás seguro de limpiar TODAS las migraciones? (s/N): " confirm
    if [[ $confirm == [sS] ]]; then
        python manage.py migrate_master --action=clean
    else
        echo "Operación cancelada."
    fi
}

reset_complete() {
    print_warning "ATENCIÓN: Esto eliminará TODOS los datos de la base de datos"
    read -p "¿Estás completamente seguro? (s/N): " confirm
    if [[ $confirm == [sS] ]]; then
        python manage.py migrate_master --action=reset
    else
        echo "Operación cancelada."
    fi
}

show_status() {
    print_step "📊 Mostrando estado de migraciones..."
    python manage.py migrate_master --action=status
}

# Programa principal
main() {
    # Verificar entorno
    check_environment
    
    echo -e "${CYAN}===============================================${NC}"
    echo -e "${YELLOW}🔥 SISTEMA MAESTRO DE MIGRACIONES 🔥${NC}"
    echo -e "${GREEN}Un script para dominarlas a todas 💍${NC}"
    echo -e "${CYAN}===============================================${NC}"
    
    while true; do
        show_menu
        read -p "Selecciona una opción (1-7): " choice
        
        case $choice in
            1)
                complete_migration
                ;;
            2)
                create_migrations
                ;;
            3)
                apply_migrations
                ;;
            4)
                clean_migrations
                ;;
            5)
                reset_complete
                ;;
            6)
                show_status
                ;;
            7)
                print_success "👋 ¡Hasta luego!"
                break
                ;;
            *)
                print_warning "Opción no válida. Selecciona del 1 al 7."
                ;;
        esac
        
        if [ "$choice" != "7" ]; then
            echo ""
            read -p "Presiona Enter para continuar..."
            clear
        fi
    done
    
    echo ""
    echo -e "${CYAN}===============================================${NC}"
    echo -e "${GREEN}🎉 Script de migraciones finalizado${NC}"
    echo -e "${CYAN}===============================================${NC}"
}

# Ejecutar programa principal
main
