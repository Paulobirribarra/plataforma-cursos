"""
Comando para poblar planes de membresía
"""
from usuarios.management.commands.base_populate import BasePopulateCommand
from membresias.models import MembershipPlan

class Command(BasePopulateCommand):
    help = 'Poblar planes de membresía del sistema'
    
    def handle(self, *args, **options):
        self.start_populate("Membresías")
        
        # Limpiar datos si se solicita
        if options['clean']:
            self.clean_data([MembershipPlan])
        
        # Ejecutar poblado dentro de transacción
        self.execute_with_transaction(self._create_membership_plans, options)
        
        self.finish_populate("Membresías")
    
    def _create_membership_plans(self, options):
        """Crear los planes de membresía"""
        
        planes = [
            {
                "name": "Básico",
                "slug": "basico",
                "price": 19990,
                "courses_per_month": 1,
                "discount_percentage": 0,
                "consultations": 1,
                "telegram_level": "basic",
                "description": "Perfecto para empezar tu aprendizaje financiero con acceso controlado.",
                "features": [
                    "1 curso mensual",
                    "Acceso a Telegram básico",
                    "1 asesoría grupal mensual",
                    "Soporte estándar",
                    "Acceso a cursos gratuitos ilimitado",
                ],
                "is_active": True,
            },
            {
                "name": "Intermedio",
                "slug": "intermedio",
                "price": 39990,
                "courses_per_month": 3,
                "discount_percentage": 10,
                "consultations": 2,
                "telegram_level": "intermediate",
                "description": "Para quienes buscan acelerar su educación financiera con más recursos.",
                "features": [
                    "3 cursos mensuales",
                    "10% descuento en cursos adicionales",
                    "Acceso a Telegram intermedio",
                    "2 asesorías grupales mensuales", 
                    "Soporte prioritario",
                    "Acceso a cursos gratuitos ilimitado",
                    "Webinars exclusivos mensuales",
                ],
                "is_active": True,
            },
            {
                "name": "Premium",
                "slug": "premium", 
                "price": 69990,
                "courses_per_month": 99,  # Ilimitado representado como 99
                "discount_percentage": 20,
                "consultations": 4,
                "telegram_level": "premium",
                "description": "La experiencia completa con acceso ilimitado y máximo apoyo personalizado.",
                "features": [
                    "Cursos ilimitados",
                    "20% descuento en cursos premium",
                    "Acceso completo a Telegram premium",
                    "4 asesorías mensuales (2 grupales + 2 individuales)",
                    "Soporte VIP 24/7",
                    "Acceso anticipado a nuevos cursos",
                    "Webinars exclusivos semanales",
                    "Sesiones 1:1 con expertos mensuales",
                    "Acceso a comunidad privada de inversores",
                ],
                "is_active": True,
            },
        ]
        
        for plan_data in planes:
            features = plan_data.pop('features')  # Extraer features por separado
            
            if options['force']:
                plan, created = self.update_or_create_safe(
                    MembershipPlan,
                    slug=plan_data['slug'],
                    defaults={**plan_data, 'features': features}
                )
            else:
                plan, created = self.get_or_create_safe(
                    MembershipPlan,
                    slug=plan_data['slug'],
                    defaults={**plan_data, 'features': features}
                )
            
            if plan:
                action = "creado" if created else "actualizado" if options['force'] else "ya existe"
                if options['verbose']:
                    self.log_info(f"Plan '{plan.name}' {action}")
        
        self.log_success(f"Procesados {len(planes)} planes de membresía")
