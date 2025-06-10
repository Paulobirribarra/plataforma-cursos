from usuarios.management.commands.base_populate import BasePopulateCommand
from cursos.models import Course, Category
from usuarios.models import CustomUser
from django.utils import timezone
from datetime import timedelta
import random

class Command(BasePopulateCommand):
    help = 'Poblar cursos gratuitos específicos para nuevos suscriptores'
    
    def handle(self, *args, **options):
        self.start_populate("Cursos Gratuitos")
        
        # Validar dependencias
        if not self._validate_dependencies():
            return
        
        # Ejecutar poblado dentro de transacción
        self.execute_with_transaction(self._create_free_courses, options)
        
        self.finish_populate("Cursos Gratuitos")
    
    def _validate_dependencies(self):
        """Validar que existan categorías e instructores"""
        if not Category.objects.exists():
            self.log_error("No hay categorías disponibles")
            self.log_info("Tip: Ejecuta primero: python manage.py populate_cursos")
            return False
        
        if not CustomUser.objects.filter(is_staff=True).exists():
            self.log_error("No hay usuarios staff para asignar como instructores")
            self.log_info("Tip: Crea un superusuario con: python manage.py createsuperuser")
            return False
        
        return True
    
    def _create_free_courses(self, options):
        """Crear cursos gratuitos específicos"""
        # Obtener datos necesarios
        instructores = list(CustomUser.objects.filter(is_staff=True))
        
        # Obtener o crear categorías necesarias
        categoria_inversion, _ = Category.objects.get_or_create(
            name="Inversión",
            defaults={"description": "Cursos sobre inversión y finanzas"}
        )
        
        categoria_educacion, _ = Category.objects.get_or_create(
            name="Educación Financiera",
            defaults={"description": "Bases de educación financiera para principiantes"}
        )
        
        categoria_fondos, _ = Category.objects.get_or_create(
            name="Fondos de Inversión", 
            defaults={"description": "Todo sobre fondos mutuos y de inversión"}
        )
        
        cursos_gratuitos = [
            {
                "title": "Introducción a las Finanzas Personales",
                "description": "Curso gratuito para comenzar tu educación financiera. Aprende conceptos básicos de ahorro, presupuesto y planificación financiera.",
                "base_price": 0,
                "duration_hours": 3,
                "difficulty_level": "beginner",
                "category": categoria_educacion,
            },
            {
                "title": "Primeros Pasos en Inversión",
                "description": "Descubre los conceptos fundamentales de la inversión y cómo dar tus primeros pasos en el mundo financiero.",
                "base_price": 0,
                "duration_hours": 4,
                "difficulty_level": "beginner",
                "category": categoria_inversion,
            },
            {
                "title": "¿Qué son los Fondos Mutuos?",
                "description": "Comprende qué son los fondos mutuos, cómo funcionan y por qué pueden ser una buena opción de inversión.",
                "base_price": 0,
                "duration_hours": 2,
                "difficulty_level": "beginner",
                "category": categoria_fondos,
            },
            {
                "title": "Conceptos Básicos de Riesgo",
                "description": "Aprende sobre los diferentes tipos de riesgo en las inversiones y cómo gestionarlos adecuadamente.",
                "base_price": 0,
                "duration_hours": 2.5,
                "difficulty_level": "beginner",
                "category": categoria_inversion,
            },
            {
                "title": "Tu Primera Meta Financiera",
                "description": "Curso práctico para establecer y alcanzar tu primera meta financiera. Incluye herramientas y estrategias.",
                "base_price": 0,
                "duration_hours": 3.5,
                "difficulty_level": "beginner",
                "category": categoria_educacion,
            },
            {
                "title": "Errores Comunes en Inversión",
                "description": "Conoce los errores más frecuentes que cometen los inversores principiantes y cómo evitarlos.",
                "base_price": 0,
                "duration_hours": 2,
                "difficulty_level": "beginner",
                "category": categoria_inversion,
            },
        ]
        
        for curso_data in cursos_gratuitos:
            course_defaults = {
                'description': curso_data['description'],
                'base_price': curso_data['base_price'],
                'duration_minutes': curso_data['duration_hours'] * 60,  # Convertir horas a minutos
                'category': curso_data['category'],
                'created_by': random.choice(instructores),
                'is_available': True,
                'is_visible': True,
                'is_free': True,  # Marcar como gratuito
                'created_at': timezone.now() - timedelta(days=random.randint(1, 15))
            }
            
            if options['force']:
                course, created = self.update_or_create_safe(
                    Course,
                    title=curso_data['title'],
                    defaults=course_defaults
                )
            else:
                course, created = self.get_or_create_safe(
                    Course,
                    title=curso_data['title'],
                    defaults=course_defaults
                )
            
            if course and options['verbose']:
                action = "creado" if created else "actualizado" if options['force'] else "ya existe"
                self.log_info(f"Curso gratuito '{course.title}' {action}")
        
        # Estadísticas finales
        total_free = Course.objects.filter(base_price=0).count()
        
        self.log_success(f"Procesados {len(cursos_gratuitos)} cursos gratuitos")
        self.log_info(f"Total cursos gratuitos en sistema: {total_free}")