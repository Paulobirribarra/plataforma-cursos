from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from usuarios.models import CustomUser
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Poblar usuarios de prueba para testing de newsletter/boletines'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cantidad',
            type=int,
            default=10,
            help='Cantidad de usuarios a crear (máximo 10)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar la creación incluso si ya existen usuarios de prueba'
        )

    def handle(self, *args, **options):
        cantidad = min(options['cantidad'], 10)  # Máximo 10 usuarios
        force = options['force']
        
        self.stdout.write(self.style.SUCCESS('=== POBLANDO USUARIOS PARA NEWSLETTER ===\n'))
        
        # Verificar si ya existen usuarios de prueba
        usuarios_prueba = User.objects.filter(email__startswith='prueba').count()
        if usuarios_prueba > 0 and not force:
            self.stdout.write(
                self.style.WARNING(
                    f'Ya existen {usuarios_prueba} usuarios de prueba. '
                    'Usa --force para recrearlos'
                )
            )
            return
        
        # Si forzamos, eliminar usuarios de prueba existentes
        if force:
            User.objects.filter(email__startswith='prueba').delete()
            self.stdout.write(self.style.WARNING('Usuarios de prueba existentes eliminados\n'))
        
        # Datos base para usuarios
        usuarios_data = [
            {
                'nombre': 'Ana García',
                'email': 'prueba1@ejemplo.com',
                'suscrito': True,
                'premium': False
            },
            {
                'nombre': 'Carlos López',
                'email': 'prueba2@ejemplo.com',
                'suscrito': True,
                'premium': True
            },
            {
                'nombre': 'María Rodríguez',
                'email': 'prueba3@ejemplo.com',
                'suscrito': False,
                'premium': False
            },
            {
                'nombre': 'Juan Pérez',
                'email': 'prueba4@ejemplo.com',
                'suscrito': True,
                'premium': False
            },
            {
                'nombre': 'Laura Martínez',
                'email': 'prueba5@ejemplo.com',
                'suscrito': True,
                'premium': True
            },
            {
                'nombre': 'Roberto Silva',
                'email': 'prueba6@ejemplo.com',
                'suscrito': False,
                'premium': False
            },
            {
                'nombre': 'Carmen Flores',
                'email': 'prueba7@ejemplo.com',
                'suscrito': True,
                'premium': False
            },
            {
                'nombre': 'Diego Torres',
                'email': 'prueba8@ejemplo.com',
                'suscrito': True,
                'premium': True
            },
            {
                'nombre': 'Patricia Luna',
                'email': 'prueba9@ejemplo.com',
                'suscrito': False,
                'premium': False
            },
            {
                'nombre': 'Fernando Castro',
                'email': 'prueba10@ejemplo.com',
                'suscrito': True,
                'premium': False
            }
        ]
        
        usuarios_creados = 0
        suscriptores = 0
        premium = 0
        
        for i in range(cantidad):
            data = usuarios_data[i]
            
            try:
                # Crear usuario
                usuario = User.objects.create_user(
                    email=data['email'],
                    password='TestPassword123!',
                    first_name=data['nombre'].split()[0],
                    last_name=' '.join(data['nombre'].split()[1:]),
                    full_name=data['nombre'],
                    suscrito_newsletter=data['suscrito'],
                    is_email_verified=True,
                    is_active=True
                )
                
                usuarios_creados += 1
                if data['suscrito']:
                    suscriptores += 1
                
                # Si es premium, crear membresía (esto es opcional y depende de tu modelo de membresías)
                if data['premium']:
                    premium += 1
                    # Aquí podrías crear una membresía activa si tienes el modelo configurado
                    # from membresias.models import Membership, MembershipPlan
                    # plan = MembershipPlan.objects.first()
                    # if plan:
                    #     Membership.objects.create(
                    #         user=usuario,
                    #         plan=plan,
                    #         status='active',
                    #         start_date=timezone.now(),
                    #         end_date=timezone.now() + timezone.timedelta(days=30)
                    #     )
                
                estado_suscripcion = "✅ Suscrito" if data['suscrito'] else "❌ No suscrito"
                estado_premium = " (Premium)" if data['premium'] else ""
                
                self.stdout.write(
                    f"  ✅ {data['nombre']} - {data['email']} - {estado_suscripcion}{estado_premium}"
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ❌ Error creando {data['email']}: {str(e)}")
                )
        
        # Resumen
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'RESUMEN DE USUARIOS CREADOS:'))
        self.stdout.write(f'• Total usuarios creados: {usuarios_creados}')
        self.stdout.write(f'• Suscriptores al newsletter: {suscriptores}')
        self.stdout.write(f'• No suscriptores: {usuarios_creados - suscriptores}')
        self.stdout.write(f'• Usuarios premium: {premium}')
        
        # Estadísticas finales del sistema
        total_usuarios = User.objects.count()
        total_suscriptores = User.objects.filter(suscrito_newsletter=True).count()
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('ESTADÍSTICAS DEL SISTEMA:'))
        self.stdout.write(f'• Total usuarios en el sistema: {total_usuarios}')
        self.stdout.write(f'• Total suscriptores al newsletter: {total_suscriptores}')
        self.stdout.write(f'• Porcentaje de suscripción: {(total_suscriptores/total_usuarios*100):.1f}%')
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('CREDENCIALES DE PRUEBA:'))
        self.stdout.write('• Email: cualquiera de los emails creados')
        self.stdout.write('• Password: TestPassword123!')
        
        self.stdout.write('\n' + self.style.SUCCESS('✅ USUARIOS DE PRUEBA CREADOS EXITOSAMENTE'))
        self.stdout.write(
            self.style.WARNING(
                '\n💡 CONSEJO: Puedes editar estos emails desde el admin de Django '
                'para usar tus propios correos y recibir los boletines de prueba.'
            )
        )
