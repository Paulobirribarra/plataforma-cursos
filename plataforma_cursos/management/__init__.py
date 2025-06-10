import os
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.apps import apps
from django.conf import settings
from django.db import connection, transaction

class BaseMigrationCommand(BaseCommand):
    """Clase base para comandos de migración con funcionalidades comunes."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apps_to_migrate = [
            'usuarios',
            'membresias', 
            'cursos',
            'pagos',
            'plataforma_cursos'
        ]
    
    def add_common_arguments(self, parser):
        """Añade argumentos comunes para comandos de migración."""
        parser.add_argument(
            '--app',
            type=str,
            help='Aplicación específica a migrar'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecuta en modo prueba sin aplicar cambios'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza la ejecución sin confirmación'
        )
    
    def get_migration_status(self):
        """Obtiene el estado de las migraciones."""
        status = {}
        for app_name in self.apps_to_migrate:
            try:
                app_config = apps.get_app_config(app_name)
                status[app_name] = {
                    'exists': True,
                    'migrations_dir': os.path.join(app_config.path, 'migrations'),
                    'has_migrations': self._has_migrations(app_name)
                }
            except Exception as e:
                status[app_name] = {
                    'exists': False,
                    'error': str(e)
                }
        return status
    
    def _has_migrations(self, app_name):
        """Verifica si una app tiene archivos de migración."""
        try:
            app_config = apps.get_app_config(app_name)
            migrations_dir = os.path.join(app_config.path, 'migrations')
            if not os.path.exists(migrations_dir):
                return False
            
            migration_files = [
                f for f in os.listdir(migrations_dir) 
                if f.endswith('.py') and f != '__init__.py'
            ]
            return len(migration_files) > 0
        except:
            return False
    
    def create_migration(self, app_name, migration_name=None):
        """Crea una nueva migración para una app."""
        try:
            cmd_args = [app_name]
            if migration_name:
                cmd_args.extend(['--name', migration_name])
            
            self.stdout.write(f"📝 Creando migración para {app_name}...")
            call_command('makemigrations', *cmd_args, verbosity=1)
            return True
        except Exception as e:
            self.stderr.write(f"❌ Error creando migración para {app_name}: {e}")
            return False
    
    def apply_migration(self, app_name=None):
        """Aplica migraciones."""
        try:
            if app_name:
                self.stdout.write(f"🚀 Aplicando migraciones para {app_name}...")
                call_command('migrate', app_name, verbosity=1)
            else:
                self.stdout.write("🚀 Aplicando todas las migraciones...")
                call_command('migrate', verbosity=1)
            return True
        except Exception as e:
            self.stderr.write(f"❌ Error aplicando migraciones: {e}")
            return False
    
    def show_migration_plan(self, app_name=None):
        """Muestra el plan de migraciones."""
        try:
            if app_name:
                call_command('showmigrations', app_name, verbosity=2)
            else:
                call_command('showmigrations', verbosity=2)
            return True
        except Exception as e:
            self.stderr.write(f"❌ Error mostrando plan de migraciones: {e}")
            return False
    
    def reset_migrations(self, app_name):
        """Resetea las migraciones de una app (PELIGROSO)."""
        try:
            with transaction.atomic():
                # Marca como no aplicadas en la tabla django_migrations
                from django.db import connection
                cursor = connection.cursor()
                cursor.execute(
                    "DELETE FROM django_migrations WHERE app = %s", 
                    [app_name]
                )
                
                # Elimina archivos de migración (excepto __init__.py)
                app_config = apps.get_app_config(app_name)
                migrations_dir = os.path.join(app_config.path, 'migrations')
                
                if os.path.exists(migrations_dir):
                    for file in os.listdir(migrations_dir):
                        if file.endswith('.py') and file != '__init__.py':
                            file_path = os.path.join(migrations_dir, file)
                            os.remove(file_path)
                            self.stdout.write(f"🗑️  Eliminado: {file}")
                
                self.stdout.write(f"✅ Migraciones de {app_name} reseteadas")
                return True
                
        except Exception as e:
            self.stderr.write(f"❌ Error reseteando migraciones de {app_name}: {e}")
            return False
    
    def check_database_connection(self):
        """Verifica la conexión a la base de datos."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except Exception as e:
            self.stderr.write(f"❌ Error de conexión a BD: {e}")
            return False
    
    def print_separator(self, title=""):
        """Imprime un separador visual."""
        if title:
            self.stdout.write(f"\n{'='*60}")
            self.stdout.write(f"  {title}")
            self.stdout.write(f"{'='*60}")
        else:
            self.stdout.write(f"{'='*60}")
    
    def confirm_action(self, message):
        """Solicita confirmación del usuario."""
        response = input(f"{message} (s/N): ").lower().strip()
        return response in ['s', 'si', 'sí', 'y', 'yes']
    
    def print_migration_status(self):
        """Imprime el estado de todas las migraciones."""
        self.print_separator("ESTADO DE MIGRACIONES")
        status = self.get_migration_status()
        
        for app_name, app_status in status.items():
            if app_status.get('exists', False):
                has_migrations = app_status.get('has_migrations', False)
                status_icon = "✅" if has_migrations else "⚠️"
                migration_text = "Con migraciones" if has_migrations else "Sin migraciones"
                self.stdout.write(f"{status_icon} {app_name}: {migration_text}")
            else:
                self.stdout.write(f"❌ {app_name}: No encontrada")
        
        self.print_separator()