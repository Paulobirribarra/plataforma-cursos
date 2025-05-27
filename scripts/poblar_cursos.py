import os
import sys
import django
import random
from datetime import timedelta

# Agregar el directorio raíz al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plataforma_cursos.settings")
django.setup()

from cursos.models import Category, Tag, Course
from usuarios.models import CustomUser
from membresias.models import MembershipPlan
from django.utils import timezone

# Categorías de ejemplo
categorias = [
    {
        "name": "Finanzas",
        "description": "Cursos sobre finanzas personales, inversiones y contabilidad.",
    },
    {
        "name": "Marketing",
        "description": "Cursos de marketing digital, redes sociales y ventas.",
    },
    {
        "name": "Emprendimiento",
        "description": "Cómo iniciar y escalar tu propio negocio.",
    },
    {
        "name": "Tecnología",
        "description": "Programación, análisis de datos y herramientas digitales.",
    },
    {
        "name": "Desarrollo Personal",
        "description": "Habilidades blandas, liderazgo y productividad.",
    },
    {
        "name": "Diseño",
        "description": "Diseño gráfico, UI/UX y herramientas creativas.",
    },
    {
        "name": "Idiomas",
        "description": "Aprende nuevos idiomas y mejora tus habilidades comunicativas.",
    },
]

# Etiquetas de ejemplo
etiquetas = [
    # Finanzas
    "inversiones",
    "ahorro",
    "trading",
    "criptomonedas",
    "contabilidad",
    # Marketing
    "publicidad",
    "ventas",
    "redes sociales",
    "seo",
    "email marketing",
    "marketing digital",
    # Tecnología
    "python",
    "javascript",
    "excel",
    "data science",
    "web development",
    "programación", 
    # Desarrollo Personal
    "liderazgo",
    "productividad",
    "comunicación",
    "negociación",
    # Emprendimiento
    "negocios",
    "emprender",
    "startup",
    "planificación",
    # Diseño
    "diseño gráfico",
    "ui/ux",
    "photoshop",
    "illustrator",
    # Idiomas
    "inglés",
    "español",
    "portugués",
    "alemán",
]

# Cursos de ejemplo
cursos = [
    # Finanzas
    {
        "title": "Introducción a Finanzas Personales",
        "description": "Aprende a gestionar tu dinero y planificar tu futuro financiero.",
        "category": "Finanzas",
        "base_price": 0,
        "is_free": True,
        "is_available": True,
        "is_visible": True,
        "duration_minutes": 90,
        "tags": ["inversiones", "ahorro"],
        "special_discount_percentage": 0.0,
        "membership_required": False,
    },
    {
        "title": "Trading para Principiantes",
        "description": "Aprende los fundamentos del trading y análisis técnico.",
        "category": "Finanzas",
        "base_price": 49990,
        "is_free": False,
        "is_available": True,
        "is_visible": True,
        "duration_minutes": 180,
        "tags": ["trading", "inversiones"],
        "special_discount_percentage": 10.0,
        "membership_required": True,
    },
    # Marketing
    {
        "title": "Marketing Digital para Emprendedores",
        "description": "Domina las redes sociales y haz crecer tu negocio.",
        "category": "Marketing",
        "base_price": 19990,
        "is_free": False,
        "is_available": True,
        "is_visible": True,
        "duration_minutes": 120,
        "tags": ["publicidad", "ventas", "redes sociales"],
        "special_discount_percentage": 10.0,
        "membership_required": False,
    },
    {
        "title": "SEO Avanzado",
        "description": "Técnicas avanzadas de posicionamiento en buscadores.",
        "category": "Marketing",
        "base_price": 39990,
        "is_free": False,
        "is_available": True,
        "is_visible": True,
        "duration_minutes": 150,
        "tags": ["seo", "marketing digital"],
        "special_discount_percentage": 15.0,
        "membership_required": True,
    },
    # Tecnología
    {
        "title": "Python desde Cero",
        "description": "Aprende a programar en Python, el lenguaje más demandado.",
        "category": "Tecnología",
        "base_price": 29990,
        "is_free": False,
        "is_available": True,
        "is_visible": True,
        "duration_minutes": 180,
        "tags": ["python", "programación"],
        "special_discount_percentage": 15.0,
        "membership_required": False,
    },
    {
        "title": "Data Science con Python",
        "description": "Análisis de datos y machine learning con Python.",
        "category": "Tecnología",
        "base_price": 59990,
        "is_free": False,
        "is_available": True,
        "is_visible": True,
        "duration_minutes": 240,
        "tags": ["python", "data science"],
        "special_discount_percentage": 20.0,
        "membership_required": True,
    },
    # Desarrollo Personal
    {
        "title": "Liderazgo y Productividad",
        "description": "Desarrolla habilidades para liderar equipos y ser más productivo.",
        "category": "Desarrollo Personal",
        "base_price": 0,
        "is_free": True,
        "is_available": True,
        "is_visible": True,
        "duration_minutes": 60,
        "tags": ["liderazgo", "productividad"],
        "special_discount_percentage": 0.0,
        "membership_required": False,
    },
    # Emprendimiento
    {
        "title": "Emprende tu Negocio",
        "description": "Guía paso a paso para lanzar tu emprendimiento.",
        "category": "Emprendimiento",
        "base_price": 39990,
        "is_free": False,
        "is_available": True,
        "is_visible": True,
        "duration_minutes": 150,
        "tags": ["negocios", "emprender"],
        "special_discount_percentage": 20.0,
        "membership_required": False,
    },
    # Diseño
    {
        "title": "Diseño Gráfico con Photoshop",
        "description": "Aprende a crear diseños profesionales con Photoshop.",
        "category": "Diseño",
        "base_price": 34990,
        "is_free": False,
        "is_available": True,
        "is_visible": True,
        "duration_minutes": 160,
        "tags": ["diseño gráfico", "photoshop"],
        "special_discount_percentage": 15.0,
        "membership_required": True,
    },
    # Idiomas
    {
        "title": "Inglés para Negocios",
        "description": "Mejora tu inglés para el entorno profesional.",
        "category": "Idiomas",
        "base_price": 29990,
        "is_free": False,
        "is_available": True,
        "is_visible": True,
        "duration_minutes": 120,
        "tags": ["inglés", "negocios"],
        "special_discount_percentage": 10.0,
        "membership_required": False,
    },
]


def poblar():
    # Crear categorías
    cat_objs = {}
    for cat in categorias:
        obj, created = Category.objects.get_or_create(
            name=cat["name"], defaults={"description": cat["description"]}
        )
        cat_objs[cat["name"]] = obj
    print(f"Categorías creadas: {list(cat_objs.keys())}")

    # Crear etiquetas
    tag_objs = {}
    for tag in etiquetas:
        obj, created = Tag.objects.get_or_create(name=tag)
        tag_objs[tag] = obj
    print(f"Etiquetas creadas: {list(tag_objs.keys())}")

    # Seleccionar un usuario staff para 'created_by'
    staff_user = CustomUser.objects.filter(is_staff=True).first()
    if not staff_user:
        print("No hay usuarios staff. Crea uno antes de poblar cursos.")
        return

    # Obtener planes de membresía
    membership_plans = MembershipPlan.objects.filter(is_active=True)
    if not membership_plans.exists():
        print(
            "No hay planes de membresía activos. Crea al menos uno antes de poblar cursos."
        )
        return

    # Crear cursos
    for curso in cursos:
        course_obj, created = Course.objects.get_or_create(
            title=curso["title"],
            defaults={
                "description": curso["description"],
                "category": cat_objs[curso["category"]],
                "base_price": curso["base_price"],
                "is_free": curso["is_free"],
                "is_available": curso["is_available"],
                "is_visible": curso["is_visible"],
                "duration_minutes": curso["duration_minutes"],
                "created_by": staff_user,
                "special_discount_percentage": curso["special_discount_percentage"],
                "membership_required": curso["membership_required"],
            },
        )

        # Asignar etiquetas
        course_obj.tags.set([tag_objs[tag] for tag in curso["tags"]])

        # Si el curso requiere membresía, asignar planes disponibles
        if curso["membership_required"]:
            course_obj.available_membership_plans.set(membership_plans)

        course_obj.save()
        print(f"Curso {'creado' if created else 'ya existía'}: {course_obj.title}")


if __name__ == "__main__":
    poblar()
