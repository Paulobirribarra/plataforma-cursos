import os
import sys
import django

# Agregar el directorio raíz al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plataforma_cursos.settings")
django.setup()

from membresias.models import MembershipPlan, ConsultationType

def poblar_tipos_consulta():
    """
    Configura los tipos de consultas según el modelo de negocio
    """
    
    # Obtener los planes de membresía
    try:
        plan_basico = MembershipPlan.objects.get(slug="basico")
        plan_intermedio = MembershipPlan.objects.get(slug="intermedio") 
        plan_premium = MembershipPlan.objects.get(slug="premium")
    except MembershipPlan.DoesNotExist:
        print("❌ Error: Los planes de membresía no están configurados.")
        print("   Ejecuta primero: python scripts/poblar_membresias.py")
        return

    # Tipos de consulta según el modelo de negocio
    tipos_consulta = [
        {
            "name": "Asesoría Grupal",
            "slug": "asesoria-grupal",
            "description": """
            Sesión grupal de asesoría financiera donde podrás:
            • Hacer preguntas sobre inversiones
            • Recibir orientación sobre tu portafolio
            • Aprender de las consultas de otros participantes
            • Obtener estrategias generales de inversión
            
            Duración: 45 minutos
            Modalidad: Videoconferencia grupal
            Participantes: Hasta 15 personas
            """,
            "is_individual": False,
            "duration_minutes": 45,
            "plans": [plan_basico, plan_intermedio]
        },
        {
            "name": "Consulta Individual Premium",
            "slug": "consulta-individual-premium", 
            "description": """
            Sesión personalizada 1:1 con experto financiero que incluye:
            • Análisis detallado de tu situación financiera
            • Estrategia de inversión personalizada
            • Revisión de portafolio actual
            • Plan de acción específico para tus objetivos
            • Seguimiento de progreso
            
            Duración: 60 minutos
            Modalidad: Videoconferencia privada
            Incluye: Reporte personalizado post-consulta
            """,
            "is_individual": True,
            "duration_minutes": 60,
            "plans": [plan_premium]
        },
        {
            "name": "Mentorías Especializadas",
            "slug": "mentorias-especializadas",
            "description": """
            Sesiones de mentoría avanzada para temas específicos:
            • Trading avanzado
            • Análisis técnico profundo
            • Estrategias de diversificación
            • Planificación de retiro
            • Optimización fiscal
            
            Duración: 90 minutos
            Modalidad: Videoconferencia individual
            Incluye: Material especializado y templates
            """,
            "is_individual": True,
            "duration_minutes": 90,
            "plans": [plan_premium]
        }
    ]

    print("🚀 Configurando tipos de consultas...")
    
    for tipo_data in tipos_consulta:
        tipo, created = ConsultationType.objects.get_or_create(
            slug=tipo_data["slug"],
            defaults={
                "name": tipo_data["name"],
                "description": tipo_data["description"],
                "is_individual": tipo_data["is_individual"],
                "duration_minutes": tipo_data["duration_minutes"],
                "is_active": True
            }
        )
        
        # Asignar planes de membresía
        tipo.membership_plans.set(tipo_data["plans"])
        
        status = "✅ Creado" if created else "ℹ️  Actualizado"
        modalidad = "Individual" if tipo.is_individual else "Grupal"
        planes_str = ", ".join([p.name for p in tipo_data["plans"]])
        
        print(f"{status}: {tipo.name}")
        print(f"   📋 Modalidad: {modalidad}")
        print(f"   ⏱️  Duración: {tipo.duration_minutes} minutos")
        print(f"   🎯 Planes: {planes_str}")
        print()

    print("🎯 Tipos de consultas configurados exitosamente!")
    print("\n📊 Resumen del modelo de consultas:")
    print("• BÁSICO: 1 asesoría grupal mensual (45 min)")
    print("• INTERMEDIO: 2 asesorías grupales mensuales (45 min c/u)")  
    print("• PREMIUM: 1 consulta individual mensual (60 min) + mentorías especializadas")
    print("\n💡 Las consultas se pueden solicitar desde el panel de usuario.")

if __name__ == "__main__":
    poblar_tipos_consulta()
