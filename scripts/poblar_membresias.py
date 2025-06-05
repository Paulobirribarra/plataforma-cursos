import os
import sys
import django

# Agregar el directorio raíz al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plataforma_cursos.settings")
django.setup()

from membresias.models import MembershipPlan

# Planes de membresía actualizados según el nuevo modelo de negocio
planes = [
    {
        "name": "Básico",
        "slug": "basico",
        "price": 19990,
        "courses_per_month": 1,
        "discount_percentage": 0,
        "consultations": 1,
        "telegram_level": "basic",
        "description": "Perfecto para empezar tu aprendizaje financiero con acceso controlado.",
        "features": [
            "1 curso mensual",
            "Acceso a Telegram básico",
            "1 asesoría grupal mensual",
            "Soporte estándar",
            "Acceso a cursos gratuitos ilimitado",
        ],
        "is_active": True,
    },
    {
        "name": "Intermedio",
        "slug": "intermedio", 
        "price": 39990,
        "courses_per_month": 2,
        "discount_percentage": 10,
        "consultations": 2,
        "telegram_level": "intermediate",
        "description": "Para quienes buscan acelerar su aprendizaje con más recursos y descuentos.",
        "features": [
            "2 cursos mensuales",
            "Acceso a Telegram intermedio",
            "2 asesorías grupales mensuales",
            "10% descuento en cursos adicionales",
            "Soporte prioritario",
            "Acceso a webinars exclusivos",
        ],
        "is_active": True,
    },
    {
        "name": "Premium",
        "slug": "premium",
        "price": 69990,
        "courses_per_month": 999,  # Acceso ilimitado
        "discount_percentage": 15,
        "consultations": 1,
        "telegram_level": "premium",
        "description": "Acceso total con asesoría personalizada y máxima prioridad.",
        "features": [
            "Acceso total a todos los cursos",
            "Acceso a Telegram premium",
            "1 asesoría individual mensual",
            "15% descuento en servicios adicionales",
            "Prioridad en soporte técnico",
            "Acceso anticipado a nuevos cursos",
            "Sesiones de mentoría 1:1",
            "Material exclusivo y plantillas",
        ],
        "is_active": True,
    },
]


def poblar():
    for plan in planes:
        obj, created = MembershipPlan.objects.get_or_create(
            slug=plan["slug"],
            defaults={
                "name": plan["name"],
                "price": plan["price"],
                "courses_per_month": plan["courses_per_month"],
                "discount_percentage": plan["discount_percentage"],
                "consultations": plan["consultations"],
                "telegram_level": plan["telegram_level"],
                "description": plan["description"],
                "features": plan["features"],
                "is_active": plan["is_active"],
            },
        )
        print(f"Plan {'creado' if created else 'ya existía'}: {obj.name}")


if __name__ == "__main__":
    poblar()
