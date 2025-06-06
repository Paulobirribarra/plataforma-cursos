import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.apps import apps

class AppMigrationCommand(BaseCommand):
    """Clase base para comandos de migración específicos por app"""
    
    app_name = None  # Debe ser definido por cada subclase
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            choices=['create', 'apply', 'clean', 'status'],
            default='create',
            help='Acción a realizar: create, apply, clean, status'
        )

    def handle(self, *args, **options):
        if not self.app_name:
            self.stdout.write(
                self.style.ERROR('❌ app_name no definido en la subclase')
            )
            return
            
        action = options['action']
        
        self.stdout.write(
            self.style.SUCCESS(f'🔧 Gestionando migraciones para {self.app_name}...')
        )

        if action == 'create':
            self.create_migrations()
        elif action == 'apply':
            self.apply_migrations()
        elif action == 'clean':
            self.clean_migrations()
        elif action == 'status':
            self.show_status()

    def create_migrations(self):
        try:
            self.stdout.write(f'📝 Creando migraciones para {self.app_name}...')
            call_command('makemigrations', self.app_name, verbosity=2)
            self.stdout.write(
                self.style.SUCCESS(f'✅ Migraciones creadas para {self.app_name}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creando migraciones para {self.app_name}: {e}')
            )

    def apply_migrations(self):
        try:
            self.stdout.write(f'🚀 Aplicando migraciones para {self.app_name}...')
            call_command('migrate', self.app_name, verbosity=2)
            self.stdout.write(
                self.style.SUCCESS(f'✅ Migraciones aplicadas para {self.app_name}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error aplicando migraciones para {self.app_name}: {e}')
            )

    def clean_migrations(self):
        try:
            app_config = apps.get_app_config(self.app_name)
            migrations_path = os.path.join(app_config.path, 'migrations')
            
            if os.path.exists(migrations_path):
                for file in os.listdir(migrations_path):
                    if file.endswith('.py') and file != '__init__.py':
                        file_path = os.path.join(migrations_path, file)
                        os.remove(file_path)
                        self.stdout.write(f'🗑️  Eliminado: {file}')
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Migraciones de {self.app_name} limpiadas')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  No se encontró carpeta de migraciones para {self.app_name}')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error limpiando migraciones para {self.app_name}: {e}')
            )

    def show_status(self):
        try:
            self.stdout.write(f'📊 Estado de migraciones para {self.app_name}:')
            call_command('showmigrations', self.app_name, verbosity=2)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error mostrando estado para {self.app_name}: {e}')
            )
