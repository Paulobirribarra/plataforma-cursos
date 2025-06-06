#!/bin/bash
# ================================
# SISTEMA MAESTRO DE POBLADO DE DATOS - Unix/Linux/Mac
# ================================

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

echo -e "${CYAN}===============================================${NC}"
echo -e "${YELLOW}🎭 SISTEMA MAESTRO DE POBLADO DE DATOS 🎭${NC}"
echo -e "${GREEN}Plataforma Cursos - Version Unix/Linux/Mac${NC}"
echo -e "${CYAN}===============================================${NC}"
echo ""

# Verificar Python
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python no encontrado. Instala Python.${NC}"
    exit 1
fi

# Determinar comando Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

echo -e "${GREEN}✅ Python detectado: $(${PYTHON_CMD} --version)${NC}"

# Verificar Django
if ${PYTHON_CMD} manage.py check --deploy &> /dev/null; then
    echo -e "${GREEN}✅ Django configurado correctamente${NC}"
else
    echo -e "${YELLOW}⚠️  Django con advertencias pero funcional${NC}"
fi

show_menu() {
    echo ""
    echo -e "${YELLOW}🎯 OPCIONES DISPONIBLES:${NC}"
    echo ""
    echo -e "${GREEN}1. 🎉 Poblado Completo${NC}"
    echo -e "${CYAN}2. 💎 Solo Membresías${NC}"
    echo -e "${BLUE}3. 📚 Solo Cursos${NC}"
    echo -e "${WHITE}4. 📋 Solo Tipos de Consulta${NC}"
    echo -e "${WHITE}5. 🆓 Solo Cursos Gratuitos${NC}"
    echo -e "${RED}6. 🧹 Limpiar Todos los Datos${NC}"
    echo -e "${YELLOW}7. 📊 Estado Actual${NC}"
    echo -e "${WHITE}8. 🚪 Salir${NC}"
    echo ""
}

execute_command() {
    local action=$1
    local description=$2
    
    echo -e "${CYAN}⚡ Ejecutando: ${description}${NC}"
    
    if ${PYTHON_CMD} manage.py populate_master --action=${action}; then
        echo -e "${GREEN}✅ ${description} completado exitosamente!${NC}"
        return 0
    else
        echo -e "${RED}❌ Error ejecutando ${description}${NC}"
        return 1
    fi
}

show_tips() {
    echo ""
    echo -e "${YELLOW}💡 CONSEJOS POST-EJECUCIÓN:${NC}"
    echo -e "${WHITE}   • Admin Django: http://localhost:8000/admin/${NC}"
    echo -e "${WHITE}   • Para crear superusuario: ${PYTHON_CMD} manage.py createsuperuser${NC}"
}

# Loop principal
while true; do
    show_menu
    
    read -p "Selecciona una opción (1-8): " choice
    
    echo ""
    echo "=================================================="
    
    case $choice in
        1)
            execute_command "complete" "Poblado Completo del Sistema"
            ;;
        2)
            execute_command "membresias" "Poblado de Membresías"
            ;;
        3)
            execute_command "cursos" "Poblado de Cursos"
            ;;
        4)
            execute_command "tipos_consulta" "Poblado de Tipos de Consulta"
            ;;
        5)
            execute_command "cursos_gratuitos" "Poblado de Cursos Gratuitos"
            ;;
        6)
            echo -e "${RED}⚠️  ATENCIÓN: Esta acción eliminará TODOS los datos de poblado.${NC}"
            read -p "¿Estás seguro? Escribe 'CONFIRMAR' para continuar: " confirm
            
            if [ "$confirm" = "CONFIRMAR" ]; then
                execute_command "clean_all" "Limpieza de Todos los Datos"
            else
                echo -e "${YELLOW}Operación cancelada.${NC}"
            fi
            ;;
        7)
            execute_command "status" "Estado Actual del Sistema"
            ;;
        8)
            echo -e "${GREEN}¡Hasta luego! 👋${NC}"
            exit 0
            ;;
        *)
            echo -e "${YELLOW}Opción inválida. Selecciona entre 1-8.${NC}"
            continue
            ;;
    esac
    
    show_tips
    
    echo ""
    echo "=================================================="
    echo ""
    
    read -p "¿Deseas realizar otra acción? (s/n): " continue_choice
    if [ "$continue_choice" != "s" ] && [ "$continue_choice" != "S" ]; then
        echo -e "${GREEN}¡Gracias por usar el Sistema Maestro de Poblado! 🎭${NC}"
        break
    fi
done
