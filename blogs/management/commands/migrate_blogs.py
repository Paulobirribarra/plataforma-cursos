from usuarios.management.commands.base_migration import AppMigrationCommand

class Command(AppMigrationCommand):
    help = 'Comando específico para migraciones de la app blogs'
    app_name = 'blogs'
