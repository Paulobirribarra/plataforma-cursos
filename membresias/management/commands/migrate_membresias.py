from usuarios.management.commands.base_migration import AppMigrationCommand

class Command(AppMigrationCommand):
    help = 'Comando específico para migraciones de la app membresias'
    app_name = 'membresias'
