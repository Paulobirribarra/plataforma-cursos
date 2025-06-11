from django.core.management.base import BaseCommand
from cursos.models import Course, Category
from membresias.models import MembershipPlan
from usuarios.models import CustomUser
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Poblar cursos de recompensa específicos para membresía Intermedio'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar recreación de cursos existentes'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar información detallada'
        )
    
    def handle(self, *args, **options):
        self.stdout.write("🔄 Iniciando creación de cursos de recompensa Intermedio...")
        
        # Validar dependencias
        if not self._validate_dependencies():
            return
        
        # Crear cursos
        self._create_intermediate_reward_courses(options)
        
        self.stdout.write(
            self.style.SUCCESS("✅ Proceso completado")
        )
    
    def _validate_dependencies(self):
        """Validar que existan categorías, instructores y plan Intermedio"""
        if not Category.objects.exists():
            self.stdout.write(
                self.style.ERROR("❌ No hay categorías disponibles")
            )
            return False
        
        if not CustomUser.objects.filter(is_staff=True).exists():
            self.stdout.write(
                self.style.ERROR("❌ No hay usuarios staff para asignar como instructores")
            )
            return False
        
        if not MembershipPlan.objects.filter(slug='intermedio').exists():
            self.stdout.write(
                self.style.ERROR("❌ No existe el plan de membresía 'Intermedio'")
            )
            return False
        
        return True
    
    def _create_intermediate_reward_courses(self, options):
        """Crear cursos de recompensa específicos para plan Intermedio"""
        # Obtener datos necesarios
        instructores = list(CustomUser.objects.filter(is_staff=True))
        plan_intermedio = MembershipPlan.objects.get(slug='intermedio')
        
        # Obtener o crear categorías necesarias
        categoria_inversion, _ = Category.objects.get_or_create(
            name="Inversión",
            defaults={"description": "Cursos sobre inversión y finanzas"}
        )
        
        categoria_trading, _ = Category.objects.get_or_create(
            name="Trading",
            defaults={"description": "Cursos especializados en trading y análisis de mercados"}
        )
        
        categoria_planificacion, _ = Category.objects.get_or_create(
            name="Planificación Financiera",
            defaults={"description": "Cursos sobre planificación y estrategias financieras"}
        )
        
        cursos_intermedio = [
            {
                "title": "Estrategias de Inversión Intermedia",
                "description": "Profundiza en estrategias de inversión más sofisticadas. Aprende sobre diversificación, análisis de riesgo-retorno y construcción de portafolios balanceados.",
                "base_price": 75000,
                "duration_hours": 6,
                "category": categoria_inversion,
            },
            {
                "title": "Análisis Fundamental de Empresas",
                "description": "Aprende a analizar estados financieros, evaluar empresas y tomar decisiones de inversión basadas en fundamentos sólidos.",
                "base_price": 85000,
                "duration_hours": 8,
                "category": categoria_inversion,
            },
            {
                "title": "Trading de Mediano Plazo",
                "description": "Estrategias de trading para posiciones de mediano plazo. Incluye análisis técnico avanzado y gestión de riesgo profesional.",
                "base_price": 95000,
                "duration_hours": 7,
                "category": categoria_trading,
            },
            {
                "title": "Planificación Financiera Avanzada",
                "description": "Técnicas avanzadas de planificación financiera personal. Incluye seguros, pensiones, optimización fiscal y planificación patrimonial.",
                "base_price": 80000,
                "duration_hours": 9,
                "category": categoria_planificacion,
            },
        ]
        
        cursos_creados = 0
        
        for curso_data in cursos_intermedio:
            course_defaults = {
                'description': curso_data['description'],
                'base_price': curso_data['base_price'],
                'duration_minutes': curso_data['duration_hours'] * 60,
                'category': curso_data['category'],
                'created_by': random.choice(instructores),
                'is_available': True,
                'is_visible': True,
                'is_free': False,
                'is_membership_reward': True,
                'created_at': timezone.now() - timedelta(days=random.randint(1, 30))
            }
            
            if options['force']:
                course, created = Course.objects.update_or_create(
                    title=curso_data['title'],
                    defaults=course_defaults
                )
            else:
                course, created = Course.objects.get_or_create(
                    title=curso_data['title'],
                    defaults=course_defaults
                )
            
            if course:
                # Asociar el curso al plan Intermedio
                course.reward_for_plans.add(plan_intermedio)
                cursos_creados += 1
                
                if options['verbose']:
                    action = "creado" if created else "actualizado" if options['force'] else "ya existe"
                    self.stdout.write(f"   - Curso '{course.title}' {action}")
        
        # Estadísticas finales
        total_reward_courses = Course.objects.filter(
            is_membership_reward=True, 
            reward_for_plans=plan_intermedio
        ).count()
        
        self.stdout.write(
            self.style.SUCCESS(f"✅ Procesados {len(cursos_intermedio)} cursos de recompensa para Intermedio")
        )
        self.stdout.write(f"📊 Total cursos de recompensa para Intermedio: {total_reward_courses}")
        self.stdout.write("💡 Los usuarios con membresía Intermedio pueden reclamar hasta 2 de estos cursos")
