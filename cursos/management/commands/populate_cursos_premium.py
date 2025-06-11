from django.core.management.base import BaseCommand
from cursos.models import Course, Category
from membresias.models import MembershipPlan
from usuarios.models import CustomUser
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Poblar cursos de recompensa específicos para membresía Premium'
    
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
        self.stdout.write("🔄 Iniciando creación de cursos de recompensa Premium...")
        
        # Validar dependencias
        if not self._validate_dependencies():
            return
        
        # Crear cursos
        self._create_premium_reward_courses(options)
        
        self.stdout.write(
            self.style.SUCCESS("✅ Proceso completado")
        )
    
    def _validate_dependencies(self):
        """Validar que existan categorías, instructores y plan Premium"""
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
        
        if not MembershipPlan.objects.filter(slug='premium').exists():
            self.stdout.write(
                self.style.ERROR("❌ No existe el plan de membresía 'Premium'")
            )
            return False
        
        return True
    
    def _create_premium_reward_courses(self, options):
        """Crear cursos de recompensa específicos para plan Premium"""
        # Obtener datos necesarios
        instructores = list(CustomUser.objects.filter(is_staff=True))
        plan_premium = MembershipPlan.objects.get(slug='premium')
        
        # Obtener o crear categorías necesarias
        categoria_trading_avanzado, _ = Category.objects.get_or_create(
            name="Trading Avanzado",
            defaults={"description": "Cursos especializados en trading profesional y técnicas avanzadas"}
        )
        
        categoria_fintech, _ = Category.objects.get_or_create(
            name="Fintech",
            defaults={"description": "Cursos sobre tecnología financiera y innovación"}
        )
        
        categoria_derivados, _ = Category.objects.get_or_create(
            name="Derivados Financieros",
            defaults={"description": "Cursos especializados en instrumentos derivados"}
        )
        
        cursos_premium = [
            {
                "title": "Trading Algorítmico y Automatización",
                "description": "Curso avanzado sobre trading algorítmico. Aprende a crear bots de trading, backtesting y automatización de estrategias financieras.",
                "base_price": 150000,
                "duration_hours": 12,
                "category": categoria_trading_avanzado,
            },
            {
                "title": "Derivados Financieros: Opciones y Futuros",
                "description": "Domina los instrumentos derivados más complejos. Opciones, futuros, swaps y estrategias de cobertura profesional.",
                "base_price": 180000,
                "duration_hours": 15,
                "category": categoria_derivados,
            },
            {
                "title": "Criptomonedas y DeFi: Estrategias Avanzadas",
                "description": "Estrategias avanzadas en el ecosistema cripto. DeFi, yield farming, análisis on-chain y gestión de riesgo en cripto.",
                "base_price": 175000,
                "duration_hours": 14,
                "category": categoria_fintech,
            },
        ]
        
        cursos_creados = 0
        
        for curso_data in cursos_premium:
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
                'created_at': timezone.now() - timedelta(days=random.randint(1, 60))
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
                # Asociar el curso al plan Premium
                course.reward_for_plans.add(plan_premium)
                cursos_creados += 1
                
                if options['verbose']:
                    action = "creado" if created else "actualizado" if options['force'] else "ya existe"
                    self.stdout.write(f"   - Curso '{course.title}' {action}")
        
        # Estadísticas finales  
        total_reward_courses = Course.objects.filter(
            is_membership_reward=True, 
            reward_for_plans=plan_premium
        ).count()
        
        self.stdout.write(
            self.style.SUCCESS(f"✅ Procesados {len(cursos_premium)} cursos de recompensa para Premium")
        )
        self.stdout.write(f"📊 Total cursos de recompensa para Premium: {total_reward_courses}")
        self.stdout.write("💡 Nota: Premium tiene acceso completo a TODOS los cursos, estos son adicionales")
