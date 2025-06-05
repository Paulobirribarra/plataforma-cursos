import os
import sys
import django

# Agregar el directorio raíz al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plataforma_cursos.settings")
django.setup()

from cursos.models import Course, Category
from usuarios.models import CustomUser

def poblar_cursos_gratuitos():
    """
    Crea cursos gratuitos específicos para nuevos suscriptores
    """
    
    # Obtener categorías existentes o crear una por defecto
    try:
        categoria_inversion = Category.objects.get(name="Inversión")
    except Category.DoesNotExist:
        categoria_inversion = Category.objects.create(
            name="Inversión",
            description="Cursos sobre inversión y finanzas"
        )
    
    try:
        categoria_fondos = Category.objects.get(name="Fondos de Inversión") 
    except Category.DoesNotExist:
        categoria_fondos = Category.objects.create(
            name="Fondos de Inversión",
            description="Cursos especializados en fondos de inversión"
        )

    # Obtener un usuario staff para asignar como creador
    staff_user = CustomUser.objects.filter(is_staff=True).first()
    if not staff_user:
        print("⚠️  No se encontró ningún usuario staff. Creando usuario admin...")
        staff_user = CustomUser.objects.create_user(
            username="admin_courses",
            email="admin@plataforma.com", 
            password="admin123",
            is_staff=True,
            is_superuser=True
        )

    # Cursos gratuitos para nuevos suscriptores
    cursos_gratuitos = [
        {
            "title": "Fondo Abeja - Introducción a la Inversión",
            "description": """
            ¡Bienvenido al mundo de las inversiones! Este curso gratuito te introducirá a los conceptos básicos 
            de inversión de manera simple y práctica. Aprenderás:
            
            • Qué son las inversiones y por qué son importantes
            • Conceptos básicos: riesgo, rentabilidad y diversificación  
            • Primeros pasos para comenzar a invertir
            • Errores comunes que debes evitar
            • Cómo establecer objetivos financieros realistas
            
            Este curso es tu primer paso hacia la libertad financiera.
            """,
            "category": categoria_inversion,
            "duration_minutes": 120,
            "tags": ["principiantes", "inversión", "finanzas", "gratuito"]
        },
        {
            "title": "Fondo Crece - Estrategias de Ahorro Inteligente",
            "description": """
            Aprende a hacer crecer tu dinero con estrategias de ahorro probadas. En este curso descubrirás:
            
            • Métodos efectivos para ahorrar dinero
            • Cómo crear un presupuesto que realmente funcione
            • Estrategias de ahorro automatizado
            • Fondos de emergencia: cuánto y cómo
            • Herramientas digitales para gestionar tus ahorros
            • Psicología del dinero y hábitos financieros
            
            Transforma tu relación con el dinero y comienza a construir riqueza.
            """,
            "category": categoria_fondos,
            "duration_minutes": 90,
            "tags": ["ahorro", "presupuesto", "finanzas", "gratuito"]
        },
        {
            "title": "Primeros Pasos en Bolsa - Curso Introductorio",
            "description": """
            ¿Te interesa la bolsa pero no sabes por dónde empezar? Este curso gratuito es perfecto para ti:
            
            • Qué es la bolsa de valores y cómo funciona
            • Tipos de instrumentos financieros
            • Cómo leer gráficos básicos
            • Análisis fundamental vs análisis técnico
            • Brokers y plataformas de inversión
            • Tu primera inversión paso a paso
            
            Al final del curso estarás listo para dar tus primeros pasos en el mercado bursátil.
            """,
            "category": categoria_inversion,
            "duration_minutes": 150,
            "tags": ["bolsa", "trading", "principiantes", "gratuito"]
        },
        {
            "title": "Educación Financiera Personal",
            "description": """
            Un curso fundamental sobre educación financiera que todo adulto debería tomar:
            
            • Principios básicos de finanzas personales
            • Cómo manejar deudas de manera inteligente
            • Tarjetas de crédito: uso responsable
            • Seguros: tipos y cuándo necesitarlos
            • Planificación para el retiro
            • Impuestos básicos que debes conocer
            
            La educación financiera es la base de toda prosperidad económica.
            """,
            "category": categoria_fondos,
            "duration_minutes": 180,
            "tags": ["educación", "finanzas", "personal", "gratuito"]
        }
    ]

    print("🚀 Creando cursos gratuitos para nuevos suscriptores...")
    
    for curso_data in cursos_gratuitos:
        curso, created = Course.objects.get_or_create(
            title=curso_data["title"],
            defaults={
                "description": curso_data["description"],
                "category": curso_data["category"],
                "base_price": 0,
                "is_free": True,
                "is_available": True,
                "is_visible": True,
                "duration_minutes": curso_data["duration_minutes"],
                "created_by": staff_user,
                "membership_required": False,
                "special_discount_percentage": 0.00
            }
        )
        
        # Agregar tags si se especificaron
        if "tags" in curso_data:
            from cursos.models import Tag
            for tag_name in curso_data["tags"]:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                curso.tags.add(tag)
        
        status = "✅ Creado" if created else "ℹ️  Ya existía"
        print(f"{status}: {curso.title}")

    print("\n🎯 Cursos gratuitos configurados exitosamente!")
    print("\n📋 Resumen de cursos gratuitos creados:")
    print("• Fondo Abeja - Introducción a la Inversión (120 min)")
    print("• Fondo Crece - Estrategias de Ahorro Inteligente (90 min)")  
    print("• Primeros Pasos en Bolsa - Curso Introductorio (150 min)")
    print("• Educación Financiera Personal (180 min)")
    print("\n💡 Estos cursos están disponibles para todos los usuarios sin membresía.")

if __name__ == "__main__":
    poblar_cursos_gratuitos()
