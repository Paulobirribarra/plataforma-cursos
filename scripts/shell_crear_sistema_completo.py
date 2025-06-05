# -*- coding: utf-8 -*-
from cursos.models import Course, Category
from membresias.models import MembershipPlan
from usuarios.models import CustomUser

# Limpiar cursos existentes
Course.objects.all().delete()

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
    categoria_avanzada = Category.objects.get(name="Estrategias Avanzadas")
except Category.DoesNotExist:
    categoria_avanzada = Category.objects.create(
        name="Estrategias Avanzadas", 
        description="Cursos avanzados de inversión y trading"
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
        "description": "Conceptos básicos sobre cómo manejar tu dinero personal. Curso completamente gratuito.",
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
        "description": "Una introducción básica al mundo de las inversiones bursátiles. Curso gratuito de enganche.",
        "base_price": 0,
        "category": categoria_inversion,
        "created_by": instructor,
        "is_free": True,
        "is_membership_reward": False,
        "duration_minutes": 30,
        "is_available": True,
        "is_visible": True,
    },
]

# 2. CURSOS DE RECOMPENSA PARA PLAN BÁSICO (1 curso)
cursos_recompensa_basico = [
    {
        "title": "Fondo Abeja - Guía Completa",
        "description": "Todo lo que necesitas saber sobre el Fondo Abeja para comenzar a invertir.",
        "base_price": 15000,
        "category": categoria_fondos,
        "created_by": instructor,
        "is_free": False,
        "is_membership_reward": True,
        "duration_minutes": 90,
        "is_available": True,
        "is_visible": True,
    },
    {
        "title": "Fondo Crece - Estrategias de Crecimiento",
        "description": "Aprende cómo utilizar el Fondo Crece para hacer crecer tu patrimonio.",
        "base_price": 15000,
        "category": categoria_fondos,
        "created_by": instructor,
        "is_free": False,
        "is_membership_reward": True,
        "duration_minutes": 90,
        "is_available": True,
        "is_visible": True,
    },
    {
        "title": "Primeros Pasos en Inversiones",
        "description": "Un curso práctico para dar tus primeros pasos en el mundo de las inversiones.",
        "base_price": 12000,
        "category": categoria_inversion,
        "created_by": instructor,
        "is_free": False,
        "is_membership_reward": True,
        "duration_minutes": 75,
        "is_available": True,
        "is_visible": True,
    },
]

# 3. CURSOS DE RECOMPENSA PARA PLAN INTERMEDIO (2 cursos)
cursos_recompensa_intermedio = [
    {
        "title": "Diversificación de Portafolio Intermedio",
        "description": "Estrategias intermedias para diversificar tu portafolio de inversiones.",
        "base_price": 25000,
        "category": categoria_inversion,
        "created_by": instructor,
        "is_free": False,
        "is_membership_reward": True,
        "duration_minutes": 120,
        "is_available": True,
        "is_visible": True,
    },
    {
        "title": "Análisis Técnico Básico",
        "description": "Introducción al análisis técnico para tomar mejores decisiones de inversión.",
        "base_price": 30000,
        "category": categoria_avanzada,
        "created_by": instructor,
        "is_free": False,
        "is_membership_reward": True,
        "duration_minutes": 150,
        "is_available": True,
        "is_visible": True,
    },
    {
        "title": "Fondos Mutuos vs ETFs",
        "description": "Comparativa detallada entre fondos mutuos y ETFs para inversores intermedios.",
        "base_price": 20000,
        "category": categoria_fondos,
        "created_by": instructor,
        "is_free": False,
        "is_membership_reward": True,
        "duration_minutes": 100,
        "is_available": True,
        "is_visible": True,
    },
]

# 4. CURSOS PREMIUM (acceso completo, no de recompensa)
cursos_premium = [
    {
        "title": "Trading Avanzado",
        "description": "Estrategias avanzadas de trading para inversores experimentados. Solo plan Premium.",
        "base_price": 50000,
        "category": categoria_avanzada,
        "created_by": instructor,
        "is_free": False,
        "is_membership_reward": False,
        "duration_minutes": 180,
        "is_available": True,
        "is_visible": True,
        "membership_required": True,
    },
    {
        "title": "Análisis Fundamental Profesional",
        "description": "Curso profesional de análisis fundamental para inversiones a largo plazo.",
        "base_price": 45000,
        "category": categoria_avanzada,
        "created_by": instructor,
        "is_free": False,
        "is_membership_reward": False,
        "duration_minutes": 200,
        "is_available": True,
        "is_visible": True,
        "membership_required": True,
    },
]

# Crear cursos gratuitos
print("=== CREANDO CURSOS GRATUITOS ===")
for curso_data in cursos_gratuitos:
    curso = Course.objects.create(**curso_data)
    print(f"✓ Curso gratuito: '{curso.title}' creado")

# Crear cursos de recompensa para plan básico
print("\n=== CREANDO CURSOS DE RECOMPENSA - PLAN BÁSICO ===")
for curso_data in cursos_recompensa_basico:
    curso = Course.objects.create(**curso_data)
    curso.reward_for_plans.add(plan_basico)
    print(f"✓ Curso recompensa básico: '{curso.title}' creado")

# Crear cursos de recompensa para plan intermedio (incluye básico + intermedio)
print("\n=== CREANDO CURSOS DE RECOMPENSA - PLAN INTERMEDIO ===")
for curso_data in cursos_recompensa_intermedio:
    curso = Course.objects.create(**curso_data)
    curso.reward_for_plans.add(plan_intermedio)
    print(f"✓ Curso recompensa intermedio: '{curso.title}' creado")

# Los cursos básicos también están disponibles para plan intermedio
print("\n=== AGREGANDO CURSOS BÁSICOS A PLAN INTERMEDIO ===")
for curso in Course.objects.filter(reward_for_plans=plan_basico):
    curso.reward_for_plans.add(plan_intermedio)
    print(f"✓ Curso '{curso.title}' ahora disponible para plan intermedio")

# Crear cursos premium
print("\n=== CREANDO CURSOS PREMIUM ===")
for curso_data in cursos_premium:
    curso = Course.objects.create(**curso_data)
    curso.available_membership_plans.add(plan_premium)
    print(f"✓ Curso premium: '{curso.title}' creado")

print(f"\n=== RESUMEN ===")
print(f"📚 Total cursos gratuitos: {Course.objects.filter(is_free=True).count()}")
print(f"🎁 Total cursos de recompensa: {Course.objects.filter(is_membership_reward=True).count()}")
print(f"👑 Total cursos premium: {Course.objects.filter(membership_required=True, is_membership_reward=False).count()}")
print(f"🎯 Cursos disponibles para plan básico: {Course.objects.filter(reward_for_plans=plan_basico).count()}")
print(f"🎯 Cursos disponibles para plan intermedio: {Course.objects.filter(reward_for_plans=plan_intermedio).count()}")
print(f"📊 Total cursos creados: {Course.objects.count()}")
