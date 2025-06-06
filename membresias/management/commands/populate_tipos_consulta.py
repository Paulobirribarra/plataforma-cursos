"""
Comando para poblar tipos de consulta
"""
from usuarios.management.commands.base_populate import BasePopulateCommand
from membresias.models import MembershipPlan, ConsultationType

class Command(BasePopulateCommand):
    help = 'Poblar tipos de consulta del sistema'
    
    def handle(self, *args, **options):
        self.start_populate("Tipos de Consulta")
        
        # Limpiar datos si se solicita
        if options['clean']:
            self.clean_data([ConsultationType])
        
        # Validar dependencias
        if not self._validate_dependencies():
            return
        
        # Ejecutar poblado dentro de transacción
        self.execute_with_transaction(self._create_consultation_types, options)
        
        self.finish_populate("Tipos de Consulta")
    
    def _validate_dependencies(self):
        """Validar que existan planes de membresía"""
        required_plans = ["basico", "intermedio", "premium"]
        for slug in required_plans:
            if not MembershipPlan.objects.filter(slug=slug).exists():
                self.log_error(f"Falta el plan de membresía: {slug}")
                self.log_info("Tip: Ejecuta primero: python manage.py populate_membresias")
                return False
        return True
    
    def _create_consultation_types(self, options):
        """Crear tipos de consulta según el modelo de negocio"""
        
        # Obtener los planes de membresía
        plan_basico = MembershipPlan.objects.get(slug="basico")
        plan_intermedio = MembershipPlan.objects.get(slug="intermedio") 
        plan_premium = MembershipPlan.objects.get(slug="premium")
        
        tipos_consulta = [
            {
                "name": "Asesoría Grupal",
                "description": "Sesión de asesoría en grupo con otros miembros de la comunidad",
                "duration_minutes": 60,
                "max_participants": 20,
                "is_individual": False,
                "membership_plans": [plan_basico, plan_intermedio, plan_premium],
                "price_non_member": 15000,
                "is_active": True,
            },
            {
                "name": "Consulta Individual",
                "description": "Sesión personalizada 1:1 con un experto financiero",
                "duration_minutes": 45,
                "max_participants": 1,
                "is_individual": True,
                "membership_plans": [plan_premium],  # Solo premium
                "price_non_member": 45000,
                "is_active": True,
            },
            {
                "name": "Revisión de Portafolio",
                "description": "Análisis detallado de tu portafolio de inversiones",
                "duration_minutes": 90,
                "max_participants": 1,
                "is_individual": True,
                "membership_plans": [plan_premium],  # Solo premium
                "price_non_member": 75000,
                "is_active": True,
            },
            {
                "name": "Sesión de Trading",
                "description": "Sesión grupal para análisis de mercado y estrategias de trading",
                "duration_minutes": 75,
                "max_participants": 15,
                "is_individual": False,
                "membership_plans": [plan_intermedio, plan_premium],
                "price_non_member": 25000,
                "is_active": True,
            },
            {
                "name": "Webinar Exclusivo",
                "description": "Webinar mensual exclusivo para miembros premium",
                "duration_minutes": 120,
                "max_participants": 100,
                "is_individual": False,
                "membership_plans": [plan_premium],
                "price_non_member": 35000,
                "is_active": True,
            },
        ]
        
        for tipo_data in tipos_consulta:
            membership_plans = tipo_data.pop('membership_plans')  # Extraer planes por separado
            
            if options['force']:
                tipo, created = self.update_or_create_safe(
                    ConsultationType,
                    name=tipo_data['name'],
                    defaults=tipo_data
                )
            else:
                tipo, created = self.get_or_create_safe(
                    ConsultationType,
                    name=tipo_data['name'],
                    defaults=tipo_data
                )
            
            # Asignar planes de membresía
            if tipo:
                tipo.membership_plans.set(membership_plans)
                
                if options['verbose']:
                    action = "creado" if created else "actualizado" if options['force'] else "ya existe"
                    plan_names = [plan.name for plan in membership_plans]
                    self.log_info(f"Tipo '{tipo.name}' {action} - Planes: {', '.join(plan_names)}")
        
        self.log_success(f"Procesados {len(tipos_consulta)} tipos de consulta")
