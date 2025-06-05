# -*- coding: utf-8 -*-
from cursos.models import Course, Category
from membresias.models import MembershipPlan
from usuarios.models import CustomUser

# Obtener o crear categorías
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
        description="Cursos sobre fondos de inversión"
    )

try:
    categoria_educacion = Category.objects.get(name="Educación Financiera")
except Category.DoesNotExist:
    categoria_educacion = Category.objects.create(
        name="Educación Financiera", 
        description="Cursos básicos de educación financiera"
    )

try:
    categoria_trading = Category.objects.get(name="Trading")
except Category.DoesNotExist:
    categoria_trading = Category.objects.create(
        name="Trading", 
        description="Cursos sobre trading y análisis técnico"
    )

# Obtener instructor
try:
    instructor = CustomUser.objects.get(email="admin@local.dev")
except CustomUser.DoesNotExist:
    instructor = CustomUser.objects.create_user(
        email="instructor@local.dev",
        password="instructor123",
        first_name="Instructor",
        last_name="Principal"
    )

# Obtener planes de membresía
plan_basico = MembershipPlan.objects.get(slug="basico")
plan_intermedio = MembershipPlan.objects.get(slug="intermedio") 
plan_premium = MembershipPlan.objects.get(slug="premium")

# 1. CURSOS GRATUITOS PARA TODOS (marketing/enganche)
cursos_gratuitos = [
    {
        "title": "Introducción a las Finanzas Personales",
        "description": "Conceptos básicos de finanzas personales para comenzar tu educación financiera.",
        "base_price": 0,
        "category": categoria_educacion,
        "created_by": instructor,
        "is_free": True,
        "is_membership_reward": False,
        "duration_minutes": 45,
        "is_available": True,
        "is_visible": True,
    },
    {
        "title": "¿Qué es la Bolsa de Valores?",
        "description": "Una introducción básica al mundo de las inversiones en bolsa.",
        "base_price": 0,
        "category": categoria_inversion,
        "created_by": instructor,
        "is_free": True,
        "is_membership_reward": False,
        "duration_minutes": 30,
        "is_available": True,
        "is_visible": True,
    }
]

# 2. CURSOS DE RECOMPENSA PARA PLAN BÁSICO E INTERMEDIO
cursos_recompensa = [
    {
        "title": "Fondo Abeja - Estrategias de Inversión",
        "description": "Aprende las estrategias específicas del Fondo Abeja y cómo maximizar tus inversiones.",
        "base_price": 49990,
        "category": categoria_fondos,
        "created_by": instructor,
        "is_free": False,
        "is_membership_reward": True,
        "duration_minutes": 120,
        "is_available": True,
        "is_visible": True,
        "reward_plans": [plan_basico, plan_intermedio],
    },
    {
        "title": "Fondo Crece - Análisis Avanzado",
        "description": "Análisis profundo del Fondo Crece y técnicas de evaluación de rendimiento.",
        "base_price": 59990,
        "category": categoria_fondos,
        "created_by": instructor,
        "is_free": False,
        "is_membership_reward": True,
        "duration_minutes": 150,
        "is_available": True,
        "is_visible": True,
        "reward_plans": [plan_basico, plan_intermedio],
    },
    {
        "title": "Trading para Principiantes",
        "description": "Conceptos básicos de trading y cómo empezar a operar en los mercados.",
        "base_price": 89990,
        "category": categoria_trading,
        "created_by": instructor,
        "is_free": False,
        "is_membership_reward": True,
        "duration_minutes": 180,
        "is_available": True,
        "is_visible": True,
        "reward_plans": [plan_basico, plan_intermedio],
    },
    {
        "title": "Análisis Técnico Fundamental",
        "description": "Aprende a leer gráficos y realizar análisis técnico de acciones.",
        "base_price": 79990,
        "category": categoria_trading,
        "created_by": instructor,
        "is_free": False,
        "is_membership_reward": True,
        "duration_minutes": 200,
        "is_available": True,
        "is_visible": True,
        "reward_plans": [plan_intermedio],  # Solo para intermedio
    },
    {
        "title": "Diversificación de Portafolio",
        "description": "Estrategias avanzadas para diversificar tu portafolio de inversiones.",
        "base_price": 69990,
        "category": categoria_inversion,
        "created_by": instructor,
        "is_free": False,
        "is_membership_reward": True,
        "duration_minutes": 160,
        "is_available": True,
        "is_visible": True,
        "reward_plans": [plan_intermedio],  # Solo para intermedio
    }
]

# 3. CURSOS PREMIUM (solo para plan premium, sin restricciones)
cursos_premium = [
    {
        "title": "Estrategias de Trading Avanzado",
        "description": "Técnicas profesionales de trading utilizadas por traders institucionales.",
        "base_price": 149990,
        "category": categoria_trading,
        "created_by": instructor,
        "is_free": False,
        "is_membership_reward": False,
        "membership_required": True,
        "duration_minutes": 300,
        "is_available": True,
        "is_visible": True,
        "available_plans": [plan_premium],
    },
    {
        "title": "Análisis Fundamental Profesional",
        "description": "Análisis fundamental avanzado para evaluar empresas e inversiones.",
        "base_price": 199990,
        "category": categoria_inversion,
        "created_by": instructor,
        "is_free": False,
        "is_membership_reward": False,
        "membership_required": True,
        "duration_minutes": 250,
        "is_available": True,
        "is_visible": True,
        "available_plans": [plan_premium],
    }
]

print("=== CREANDO CURSOS GRATUITOS ===")
# Crear cursos gratuitos
for curso_data in cursos_gratuitos:
    curso, created = Course.objects.get_or_create(
        title=curso_data["title"],
        defaults=curso_data
    )
    if created:
        print(f"✓ Curso gratuito '{curso.title}' creado")
    else:
        print(f"• Curso gratuito '{curso.title}' ya existía")

print("\n=== CREANDO CURSOS DE RECOMPENSA ===")
# Crear cursos de recompensa
for curso_data in cursos_recompensa:
    reward_plans = curso_data.pop('reward_plans')
    curso, created = Course.objects.get_or_create(
        title=curso_data["title"],
        defaults=curso_data
    )
    if created:
        print(f"✓ Curso de recompensa '{curso.title}' creado")
    else:
        print(f"• Curso de recompensa '{curso.title}' ya existía")
    
    # Agregar a los planes de recompensa
    curso.reward_for_plans.set(reward_plans)

print("\n=== CREANDO CURSOS PREMIUM ===")
# Crear cursos premium
for curso_data in cursos_premium:
    available_plans = curso_data.pop('available_plans')
    curso, created = Course.objects.get_or_create(
        title=curso_data["title"],
        defaults=curso_data
    )
    if created:
        print(f"✓ Curso premium '{curso.title}' creado")
    else:
        print(f"• Curso premium '{curso.title}' ya existía")
    
    # Agregar a los planes disponibles
    curso.available_membership_plans.set(available_plans)

print("\n=== RESUMEN ===")
print(f"Cursos gratuitos: {Course.objects.filter(is_free=True).count()}")
print(f"Cursos de recompensa: {Course.objects.filter(is_membership_reward=True).count()}")
print(f"Cursos premium: {Course.objects.filter(membership_required=True, is_membership_reward=False).count()}")
print(f"Total de cursos: {Course.objects.count()}")
