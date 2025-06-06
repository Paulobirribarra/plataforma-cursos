"""
Comando maestro para poblar todos los datos del sistema
Coordina la ejecución de todos los comandos de poblado en el orden correcto
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction
from django.utils import timezone
import sys

class Command(BaseCommand):
    help = 'Comando maestro para poblar todos los datos del sistema'
    
    # Orden de ejecución basado en dependencias
    POPULATE_ORDER = [
        ('membresias', 'populate_membresias'),
        ('cursos', 'populate_cursos'), 
        ('membresias', 'populate_tipos_consulta'),
        ('cursos', 'populate_cursos_gratuitos'),
    ]
    
    ACTIONS = {
        'complete': 'Poblado completo del sistema',
        'membresias': 'Solo planes de membresía',
        'cursos': 'Solo cursos y categorías',
        'tipos_consulta': 'Solo tipos de consulta',
        'cursos_gratuitos': 'Solo cursos gratuitos',
        'clean_all': 'Limpiar todos los datos',
        'status': 'Mostrar estado actual de datos'
    }
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            choices=list(self.ACTIONS.keys()),
            default='complete',
            help='Acción a realizar'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar recreación de datos existentes'
        )
        parser.add_argument(
            '--no-transaction',
            action='store_true',
            help='No usar transacciones (para debugging)'
        )
    
    def handle(self, *args, **options):
        action = options['action']
        force = options['force']
        use_transaction = not options['no_transaction']
        
        self.log_header()
        self.stdout.write(f"🎯 Acción seleccionada: {self.ACTIONS[action]}")
        self.stdout.write("")
        
        start_time = timezone.now()
        
        try:
            if use_transaction:
                with transaction.atomic():
                    self._execute_action(action, force)
            else:
                self._execute_action(action, force)
                
            elapsed = timezone.now() - start_time
            self.stdout.write(
                self.style.SUCCESS(f"🎉 Poblado maestro completado en {elapsed.total_seconds():.2f}s")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"💥 Error en poblado maestro: {str(e)}")
            )
            if use_transaction:
                self.stdout.write(
                    self.style.WARNING("🔄 Transacción revertida automáticamente")
                )
    
    def _execute_action(self, action, force):
        """Ejecutar la acción especificada"""
        
        if action == 'complete':
            self._populate_complete(force)
        elif action == 'membresias':
            self._call_populate_command('populate_membresias', force)
        elif action == 'cursos':
            self._call_populate_command('populate_cursos', force)
        elif action == 'tipos_consulta':
            self._call_populate_command('populate_tipos_consulta', force)
        elif action == 'cursos_gratuitos':
            self._call_populate_command('populate_cursos_gratuitos', force)
        elif action == 'clean_all':
            self._clean_all_data()
        elif action == 'status':
            self._show_status()
    
    def _populate_complete(self, force):
        """Poblado completo en orden de dependencias"""
        self.stdout.write(
            self.style.HTTP_INFO("🚀 Iniciando poblado completo del sistema...")
        )
        
        for app_name, command_name in self.POPULATE_ORDER:
            self.stdout.write("")
            self.stdout.write(f"📦 Ejecutando: {command_name}")
            self._call_populate_command(command_name, force)
    
    def _call_populate_command(self, command_name, force):
        """Llamar a un comando de poblado específico"""
        try:
            options = {}
            if force:
                options['force'] = True
            
            call_command(command_name, **options)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error ejecutando {command_name}: {str(e)}")
            )
            raise
    
    def _clean_all_data(self):
        """Limpiar todos los datos del sistema"""
        self.stdout.write(
            self.style.WARNING("🧹 Limpiando todos los datos del sistema...")
        )
        
        # Importar modelos
        from cursos.models import Course, Category, Tag
        from membresias.models import MembershipPlan, ConsultationType
        
        models_to_clean = [
            Course, Category, Tag,
            MembershipPlan, ConsultationType
        ]
        
        for model in models_to_clean:
            try:
                count = model.objects.count()
                if count > 0:
                    model.objects.all().delete()
                    self.stdout.write(f"🗑️  Eliminados {count} registros de {model.__name__}")
                else:
                    self.stdout.write(f"➖ {model.__name__} ya estaba vacío")
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error limpiando {model.__name__}: {str(e)}")
                )
    
    def _show_status(self):
        """Mostrar estado actual de los datos"""
        self.stdout.write(
            self.style.HTTP_INFO("📊 Estado actual de los datos:")
        )
          # Importar modelos
        from cursos.models import Course, Category, Tag
        from membresias.models import MembershipPlan, ConsultationType
        
        stats = [
            ('Categorías de Cursos', Category.objects.count()),
            ('Tags', Tag.objects.count()),
            ('Cursos', Course.objects.count()),
            ('Cursos Gratuitos', Course.objects.filter(base_price=0).count()),
            ('Cursos de Pago', Course.objects.filter(base_price__gt=0).count()),
            ('Planes de Membresía', MembershipPlan.objects.count()),
            ('Tipos de Consulta', ConsultationType.objects.count()),
        ]
        
        self.stdout.write("")
        for name, count in stats:
            color = self.style.SUCCESS if count > 0 else self.style.WARNING
            self.stdout.write(color(f"  {name}: {count}"))
        
        self.stdout.write("")
          # Mostrar algunos ejemplos
        if Course.objects.exists():
            latest_courses = Course.objects.order_by('-created_at')[:3]
            self.stdout.write("📚 Últimos cursos creados:")
            for course in latest_courses:
                self.stdout.write(f"  • {course.title} (${course.base_price})")
        
        if MembershipPlan.objects.exists():
            plans = MembershipPlan.objects.all()
            self.stdout.write("💎 Planes de membresía:")
            for plan in plans:
                self.stdout.write(f"  • {plan.name} - ${plan.price}")
    
    def log_header(self):
        """Mostrar header del comando"""
        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write(
            self.style.SUCCESS("🎭 SISTEMA MAESTRO DE POBLADO DE DATOS 🎭")
        )
        self.stdout.write(
            self.style.HTTP_INFO("Plataforma Cursos - Automatización Total")
        )
        self.stdout.write("=" * 60)
