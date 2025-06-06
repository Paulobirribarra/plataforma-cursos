import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.apps import apps
from django.conf import settings

class Command(BaseCommand):
    help = '🔥 COMANDO MAESTRO DE MIGRACIONES - Un comando para dominarlas a todas 💍'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            choices=['complete', 'create', 'apply', 'clean', 'status', 'reset'],
            default='complete',
            help='Acción a realizar'
        )
        parser.add_argument(
            '--apps',
            nargs='*',
            default=['usuarios', 'cursos', 'pagos', 'membresias', 'blogs', 'boletines', 'carrito'],
            help='Apps específicas a procesar'
        )

    def handle(self, *args, **options):
        action = options['action']
        apps_to_process = options['apps']
        
        self.stdout.write('=' * 50)
        self.stdout.write(
            self.style.SUCCESS('🔥 SISTEMA MAESTRO DE MIGRACIONES 🔥')
        )
        self.stdout.write(
            self.style.SUCCESS('Un comando para dominarlas a todas 💍')
        )
        self.stdout.write('=' * 50)
        self.stdout.write('')

        if action == 'complete':
            self.complete_migration(apps_to_process)
        elif action == 'create':
            self.create_all_migrations(apps_to_process)
        elif action == 'apply':
            self.apply_all_migrations(apps_to_process)
        elif action == 'clean':
            self.clean_all_migrations(apps_to_process)
        elif action == 'status':
            self.show_status()
        elif action == 'reset':
            self.reset_complete(apps_to_process)

    def complete_migration(self, apps_list):
        """Migración completa - limpia, crea y aplica todas las migraciones"""
        self.stdout.write(
            self.style.WARNING('🎯 INICIANDO MIGRACIÓN COMPLETA...')
        )
        
        # Paso 1: Limpiar migraciones
        self.clean_all_migrations(apps_list)
        
        # Paso 2: Crear migraciones
        self.create_all_migrations(apps_list)
        
        # Paso 3: Aplicar migraciones
        self.apply_all_migrations()
        
        self.stdout.write(
            self.style.SUCCESS('✨ MIGRACIÓN COMPLETA EXITOSA ✨')
        )

    def create_all_migrations(self, apps_list):
        """Crear migraciones para todas las apps"""
        self.stdout.write(
            self.style.HTTP_INFO('📝 Creando migraciones para todas las apps...')
        )
        
        for app_name in apps_list:
            try:
                self.stdout.write(f'  📝 Creando migraciones para {app_name}...')
                call_command('makemigrations', app_name, verbosity=1)
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ Migraciones creadas para {app_name}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Error en {app_name}: {e}')
                )

    def apply_all_migrations(self, apps_list=None):
        """Aplicar todas las migraciones"""
        self.stdout.write(
            self.style.HTTP_INFO('🚀 Aplicando todas las migraciones...')
        )
        
        try:
            call_command('migrate', verbosity=1)
            self.stdout.write(
                self.style.SUCCESS('✅ Todas las migraciones aplicadas correctamente')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error aplicando migraciones: {e}')
            )

    def clean_all_migrations(self, apps_list):
        """Limpiar todas las migraciones de las apps especificadas"""
        self.stdout.write(
            self.style.WARNING('🧹 Limpiando migraciones existentes...')
        )
        
        for app_name in apps_list:
            try:
                app_config = apps.get_app_config(app_name)
                migrations_path = os.path.join(app_config.path, 'migrations')
                
                if os.path.exists(migrations_path):
                    migration_files = [f for f in os.listdir(migrations_path) 
                                     if f.endswith('.py') and f != '__init__.py']
                    
                    for file in migration_files:
                        file_path = os.path.join(migrations_path, file)
                        os.remove(file_path)
                    
                    if migration_files:
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✅ {len(migration_files)} archivos eliminados de {app_name}')
                        )
                    else:
                        self.stdout.write(f'  ℹ️  No hay migraciones en {app_name}')
                else:
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠️  No se encontró carpeta migrations en {app_name}')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Error limpiando {app_name}: {e}')
                )

    def show_status(self):
        """Mostrar estado actual de todas las migraciones"""
        self.stdout.write(
            self.style.HTTP_INFO('📊 Estado actual de migraciones:')
        )
        
        try:
            self.stdout.write('\n--- MIGRACIONES PENDIENTES ---')
            call_command('showmigrations', '--plan')
            
            self.stdout.write('\n--- ESTADO POR APP ---')
            call_command('showmigrations')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error mostrando estado: {e}')
            )

    def reset_complete(self, apps_list):
        """Reset completo: flush database + limpia migraciones + migración completa"""
        self.stdout.write(
            self.style.ERROR('🗄️  INICIANDO RESET COMPLETO...')
        )
        
        # Confirmar acción peligrosa
        confirm = input('⚠️  ¿Estás seguro? Esto eliminará TODOS los datos (s/N): ')
        if confirm.lower() != 's':
            self.stdout.write('Operación cancelada.')
            return
        
        try:
            # Flush database
            self.stdout.write('🗑️  Eliminando todos los datos...')
            call_command('flush', '--noinput')
            
            # Migración completa
            self.complete_migration(apps_list)
            
            self.stdout.write(
                self.style.SUCCESS('✨ RESET COMPLETO EXITOSO ✨')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error en reset: {e}')
            )
