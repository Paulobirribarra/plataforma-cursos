# -*- coding: utf-8 -*-
from membresias.models import MembershipPlan

# Limpiar planes existentes
MembershipPlan.objects.all().delete()

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
        "description": "Para usuarios que quieren acelerar su aprendizaje con más contenido y beneficios.",
        "features": [
            "2 cursos mensuales",
            "Acceso a Telegram intermedio",
            "2 asesorías grupales mensuales", 
            "10% descuento en cursos adicionales",
            "Soporte prioritario",
            "Acceso a cursos gratuitos ilimitado",
        ],
        "is_active": True,
    },
    {
        "name": "Premium",
        "slug": "premium",
        "price": 69990,
        "courses_per_month": 999,  # Acceso ilimitado
        "discount_percentage": 15,
        "consultations": 1,  # 1 asesoría individual
        "telegram_level": "premium",
        "description": "Acceso completo a toda la plataforma con beneficios exclusivos y asesoría personalizada.",
        "features": [
            "Acceso ilimitado a todos los cursos",
            "1 asesoría individual mensual",
            "Acceso a Telegram premium con contenido exclusivo",
            "15% descuento en servicios adicionales",
            "Soporte prioritario 24/7",
            "Acceso temprano a nuevos cursos",
            "Acceso a cursos gratuitos ilimitado",
        ],
        "is_active": True,
    },
]

# Crear los planes
for plan_data in planes:
    plan = MembershipPlan.objects.create(**plan_data)
    print(f"Plan '{plan.name}' creado exitosamente")

print(f"\nTotal de planes creados: {MembershipPlan.objects.count()}")
