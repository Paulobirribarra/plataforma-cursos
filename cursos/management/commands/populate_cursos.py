"""
Comando para poblar cursos, categorías y tags
"""
from usuarios.management.commands.base_populate import BasePopulateCommand
from cursos.models import Course, Category, Tag
from usuarios.models import CustomUser
from membresias.models import MembershipPlan
from django.utils import timezone
from datetime import timedelta
import random

class Command(BasePopulateCommand):
    help = 'Poblar cursos, categorías y tags del sistema'
    
    def handle(self, *args, **options):
        self.start_populate("Cursos")
        
        # Limpiar datos si se solicita
        if options['clean']:
            self.clean_data([Course, Category, Tag])
        
        # Validar dependencias
        if not self._validate_dependencies():
            return
        
        # Ejecutar poblado dentro de transacción
        self.execute_with_transaction(self._create_courses_data, options)
        
        self.finish_populate("Cursos")
    
    def _validate_dependencies(self):
        """Validar que existan usuarios instructores"""
        if not CustomUser.objects.filter(is_staff=True).exists():
            self.log_error("No hay usuarios staff para asignar como instructores")
            self.log_info("Tip: Crea un superusuario con: python manage.py createsuperuser")
            return False
        return True
    
    def _create_courses_data(self, options):
        """Crear categorías, tags y cursos"""
        
        # 1. Crear categorías
        self._create_categories(options)
        
        # 2. Crear tags
        self._create_tags(options)
        
        # 3. Crear cursos
        self._create_courses(options)
    
    def _create_categories(self, options):
        """Crear categorías de cursos"""
        
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
                "name": "Inversión",
                "description": "Estrategias de inversión en diferentes mercados.",
            },
            {
                "name": "Fondos de Inversión",
                "description": "Todo sobre fondos mutuos y de inversión.",
            },
            {
                "name": "Educación Financiera",
                "description": "Bases de educación financiera para principiantes.",
            },
            {
                "name": "Criptomonedas",
                "description": "Mundo de las criptomonedas y blockchain.",
            },
            {
                "name": "Bolsa de Valores",
                "description": "Trading e inversión en bolsa de valores.",
            },
        ]
        
        for categoria_data in categorias:
            if options['force']:
                categoria, created = self.update_or_create_safe(
                    Category,
                    name=categoria_data['name'],
                    defaults=categoria_data
                )
            else:
                categoria, created = self.get_or_create_safe(
                    Category,
                    name=categoria_data['name'],
                    defaults=categoria_data
                )
            
            if categoria and options['verbose']:
                action = "creada" if created else "actualizada" if options['force'] else "ya existe"
                self.log_info(f"Categoría '{categoria.name}' {action}")
    
    def _create_tags(self, options):
        """Crear tags para cursos"""
        
        tags = [
            "principiante", "intermedio", "avanzado", "práctico", "teórico",
            "inversión", "ahorro", "presupuesto", "deudas", "crédito",
            "bolsa", "acciones", "bonos", "derivados", "opciones",
            "bitcoin", "ethereum", "defi", "trading", "análisis técnico",
            "análisis fundamental", "gestión de riesgo", "diversificación",
            "planificación financiera", "jubilación", "seguros", "impuestos"
        ]
        
        for tag_name in tags:
            if options['force']:
                tag, created = self.update_or_create_safe(
                    Tag,
                    name=tag_name,
                    defaults={'name': tag_name}
                )
            else:
                tag, created = self.get_or_create_safe(
                    Tag,
                    name=tag_name,
                    defaults={'name': tag_name}
                )
            
            if tag and options['verbose']:
                action = "creado" if created else "actualizado" if options['force'] else "ya existe"
                self.log_info(f"Tag '{tag.name}' {action}")
    
    def _create_courses(self, options):
        """Crear cursos de ejemplo"""
        
        # Obtener datos necesarios
        categories = list(Category.objects.all())
        tags = list(Tag.objects.all())
        instructores = list(CustomUser.objects.filter(is_staff=True))
        
        if not categories or not instructores:
            self.log_error("Faltan categorías o instructores para crear cursos")
            return
        
        cursos = [
            {
                "title": "Fundamentos de Inversión",
                "description": "Aprende los conceptos básicos de inversión y cómo empezar a invertir tu dinero de manera inteligente.",
                "price": 45000,
                "duration_hours": 8,
                "difficulty_level": "beginner",
                "category": "Inversión",
                "tags": ["principiante", "inversión", "fundamentos"],
            },
            {
                "title": "Trading para Principiantes",
                "description": "Curso completo de trading desde cero, aprende a operar en los mercados financieros.",
                "price": 65000,
                "duration_hours": 12,
                "difficulty_level": "beginner",
                "category": "Bolsa de Valores",
                "tags": ["principiante", "trading", "bolsa"],
            },
            {
                "title": "Análisis Técnico Avanzado",
                "description": "Domina las técnicas avanzadas de análisis técnico para mejorar tus decisiones de inversión.",
                "price": 85000,
                "duration_hours": 16,
                "difficulty_level": "advanced",
                "category": "Bolsa de Valores",
                "tags": ["avanzado", "análisis técnico", "trading"],
            },
            {
                "title": "Criptomonedas: Guía Completa",
                "description": "Todo lo que necesitas saber sobre Bitcoin, Ethereum y el mundo de las criptomonedas.",
                "price": 55000,
                "duration_hours": 10,
                "difficulty_level": "intermediate",
                "category": "Criptomonedas",
                "tags": ["intermedio", "bitcoin", "ethereum", "criptomonedas"],
            },
            {
                "title": "Planificación Financiera Personal",
                "description": "Aprende a planificar tu futuro financiero, crear presupuestos y alcanzar tus metas económicas.",
                "price": 35000,
                "duration_hours": 6,
                "difficulty_level": "beginner",
                "category": "Educación Financiera",
                "tags": ["principiante", "planificación financiera", "presupuesto"],
            },
            {
                "title": "Fondos de Inversión Explicados",
                "description": "Comprende cómo funcionan los fondos mutuos y de inversión, y cómo elegir los mejores.",
                "price": 40000,
                "duration_hours": 7,
                "difficulty_level": "intermediate",
                "category": "Fondos de Inversión",
                "tags": ["intermedio", "fondos", "diversificación"],
            },
        ]
        
        for curso_data in cursos:
            # Buscar categoría
            try:
                category = Category.objects.get(name=curso_data['category'])
            except Category.DoesNotExist:
                category = categories[0]  # Usar primera categoría como fallback
              # Preparar datos del curso
            course_defaults = {
                'description': curso_data['description'],
                'base_price': curso_data['price'],
                'duration_minutes': curso_data['duration_hours'] * 60,  # Convertir horas a minutos
                'category': category,
                'created_by': random.choice(instructores),
                'is_available': True,
                'is_visible': True,
                'created_at': timezone.now() - timedelta(days=random.randint(1, 30))
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
            
            # Agregar tags al curso
            if course:
                course_tags = [tag for tag in tags if tag.name in curso_data['tags']]
                if course_tags:
                    course.tags.set(course_tags)
                if options['verbose']:
                    action = "creado" if created else "actualizado" if options['force'] else "ya existe"
                    self.log_info(f"Curso '{course.title}' {action} (${course.base_price})")
        
        self.log_success(f"Procesados {len(cursos)} cursos")
