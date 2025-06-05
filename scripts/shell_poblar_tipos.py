# -*- coding: utf-8 -*-
from membresias.models import ConsultationType

# Limpiar tipos de consulta existentes
ConsultationType.objects.all().delete()

# Crear tipos de consulta
tipos_consulta = [
    {
        "name": "Consulta Grupal",
        "slug": "grupal",
        "description": "Sesión de consulta en grupo con otros miembros",
        "is_individual": False,
        "duration_minutes": 60,
        "is_active": True,
    },
    {
        "name": "Consulta Individual", 
        "slug": "individual",
        "description": "Sesión de consulta personalizada uno a uno",
        "is_individual": True,
        "duration_minutes": 45,
        "is_active": True,
    }
]

for tipo_data in tipos_consulta:
    tipo = ConsultationType.objects.create(**tipo_data)
    print(f"Tipo de consulta '{tipo.name}' creado exitosamente")

print(f"\nTotal de tipos de consulta creados: {ConsultationType.objects.count()}")
