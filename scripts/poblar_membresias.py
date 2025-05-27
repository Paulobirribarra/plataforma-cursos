import os
import sys
import django

# Agregar el directorio raíz al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plataforma_cursos.settings")
django.setup()

from membresias.models import MembershipPlan

# Planes de membresía de ejemplo
planes = [
    {
        "name": "Plan Básico",
        "slug": "plan-basico",
        "price": 19990,
        "courses_per_month": 2,
        "discount_percentage": 10,
        "consultations": 2,
        "telegram_level": "basic",
        "description": "Ideal para quienes están comenzando su aprendizaje.",
        "features": [
            "Acceso a 2 cursos por mes",
            "2 consultas con instructores",
            "Soporte básico por Telegram",
            "10% de descuento en cursos adicionales",
        ],
        "is_active": True,
    },
    {
        "name": "Plan Pro",
        "slug": "plan-pro",
        "price": 39990,
        "courses_per_month": 5,
        "discount_percentage": 20,
        "consultations": 5,
        "telegram_level": "intermediate",
        "description": "Para estudiantes que buscan un aprendizaje más intensivo.",
        "features": [
            "Acceso a 5 cursos por mes",
            "5 consultas con instructores",
            "Soporte prioritario por Telegram",
            "20% de descuento en cursos adicionales",
            "Acceso a cursos premium",
        ],
        "is_active": True,
    },
    {
        "name": "Plan Premium",
        "slug": "plan-premium",
        "price": 69990,
        "courses_per_month": 10,
        "discount_percentage": 30,
        "consultations": 10,
        "telegram_level": "premium",
        "description": "La mejor experiencia de aprendizaje con acceso ilimitado.",
        "features": [
            "Acceso a 10 cursos por mes",
            "10 consultas con instructores",
            "Soporte VIP por Telegram",
            "30% de descuento en cursos adicionales",
            "Acceso a todos los cursos premium",
            "Acceso anticipado a nuevos cursos",
            "Certificados de finalización",
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
