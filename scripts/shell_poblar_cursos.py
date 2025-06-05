# -*- coding: utf-8 -*-
from cursos.models import Course, Category
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

# Obtener instructor (crear uno si no existe)
try:
    instructor = CustomUser.objects.get(email="admin@local.dev")
except CustomUser.DoesNotExist:
    instructor = CustomUser.objects.create_user(
        email="instructor@local.dev",
        password="instructor123",
        first_name="Instructor",
        last_name="Principal"
    )

# Cursos gratuitos específicos para nuevos suscriptores
cursos_gratuitos = [
    {
        "title": "Fondo Abeja - Introducción",
        "description": "Introducción básica al Fondo Abeja y sus características principales.",
        "base_price": 0,
        "category": categoria_fondos,
        "created_by": instructor,
        "is_free": True,
        "duration_minutes": 60,
        "is_available": True,
        "is_visible": True,
    },
    {
        "title": "Fondo Crece - Fundamentos",
        "description": "Fundamentos del Fondo Crece y cómo puede ayudarte a hacer crecer tu dinero.",
        "base_price": 0,
        "category": categoria_fondos,
        "created_by": instructor,
        "is_free": True,
        "duration_minutes": 60,
        "is_available": True,
        "is_visible": True,
    },
    {
        "title": "Primeros Pasos en Bolsa",
        "description": "Una guía básica para dar tus primeros pasos en el mundo de la bolsa de valores.",
        "base_price": 0,
        "category": categoria_inversion,
        "created_by": instructor,
        "is_free": True,
        "duration_minutes": 120,
        "is_available": True,
        "is_visible": True,
    },
    {
        "title": "Educación Financiera Personal",
        "description": "Conceptos básicos de educación financiera para el manejo personal del dinero.",
        "base_price": 0,
        "category": categoria_educacion,
        "created_by": instructor,
        "is_free": True,
        "duration_minutes": 120,
        "is_available": True,
        "is_visible": True,
    },
]

# Crear los cursos
for curso_data in cursos_gratuitos:
    curso, created = Course.objects.get_or_create(
        title=curso_data["title"],
        defaults=curso_data
    )
    if created:
        print(f"Curso gratuito '{curso.title}' creado exitosamente")
    else:
        print(f"Curso gratuito '{curso.title}' ya existía")

print(f"\nTotal de cursos gratuitos: {Course.objects.filter(is_free=True).count()}")
