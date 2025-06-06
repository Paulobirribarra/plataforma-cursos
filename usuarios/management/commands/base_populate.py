"""
Clase base para comandos de poblado de datos
Proporciona funcionalidad común para todos los comandos de población
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
import sys

class BasePopulateCommand(BaseCommand):
    """
    Clase base para comandos de poblado de datos
    Proporciona manejo de errores, transacciones y logging consistente
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.created_count = 0
        self.updated_count = 0
        self.skipped_count = 0
        self.errors = []
    
    def add_arguments(self, parser):
        """Argumentos comunes para todos los comandos de poblado"""
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar recreación de datos existentes'
        )
        parser.add_argument(
            '--clean',
            action='store_true', 
            help='Limpiar datos existentes antes de poblar'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar información detallada'
        )
    
    def log_success(self, message):
        """Log de éxito en verde"""
        self.stdout.write(
            self.style.SUCCESS(f"✅ {message}")
        )
    
    def log_warning(self, message):
        """Log de advertencia en amarillo"""
        self.stdout.write(
            self.style.WARNING(f"⚠️  {message}")
        )
    
    def log_error(self, message):
        """Log de error en rojo"""
        self.stdout.write(
            self.style.ERROR(f"❌ {message}")
        )
        self.errors.append(message)
    
    def log_info(self, message):
        """Log de información"""
        self.stdout.write(f"ℹ️  {message}")
    
    def log_step(self, message):
        """Log de paso en curso"""
        self.stdout.write(
            self.style.HTTP_INFO(f"⚡ {message}")
        )
    
    def start_populate(self, app_name):
        """Iniciar proceso de poblado"""
        self.log_step(f"Iniciando poblado de {app_name}...")
        self.start_time = timezone.now()
    
    def finish_populate(self, app_name):
        """Finalizar proceso de poblado"""
        elapsed = timezone.now() - self.start_time
        
        if self.errors:
            self.log_error(f"Poblado de {app_name} completado con errores:")
            for error in self.errors:
                self.log_error(f"  - {error}")
        else:
            self.log_success(f"Poblado de {app_name} completado exitosamente")
        
        self.log_info(f"Resumen:")
        self.log_info(f"  - Creados: {self.created_count}")
        self.log_info(f"  - Actualizados: {self.updated_count}") 
        self.log_info(f"  - Omitidos: {self.skipped_count}")
        self.log_info(f"  - Tiempo: {elapsed.total_seconds():.2f}s")
    
    def get_or_create_safe(self, model, defaults=None, **kwargs):
        """
        Versión segura de get_or_create con manejo de errores
        """
        try:
            obj, created = model.objects.get_or_create(
                defaults=defaults, **kwargs
            )
            if created:
                self.created_count += 1
                return obj, True
            else:
                self.skipped_count += 1
                return obj, False
        except Exception as e:
            self.log_error(f"Error creando {model.__name__}: {str(e)}")
            return None, False
    
    def update_or_create_safe(self, model, defaults=None, **kwargs):
        """
        Versión segura de update_or_create con manejo de errores
        """
        try:
            obj, created = model.objects.update_or_create(
                defaults=defaults, **kwargs
            )
            if created:
                self.created_count += 1
            else:
                self.updated_count += 1
            return obj, created
        except Exception as e:
            self.log_error(f"Error actualizando {model.__name__}: {str(e)}")
            return None, False
    
    def execute_with_transaction(self, populate_function, *args, **kwargs):
        """
        Ejecutar función de poblado dentro de una transacción
        """
        try:
            with transaction.atomic():
                return populate_function(*args, **kwargs)
        except Exception as e:
            self.log_error(f"Error en transacción: {str(e)}")
            raise
    
    def clean_data(self, models):
        """
        Limpiar datos de los modelos especificados
        """
        for model in models:
            try:
                count = model.objects.count()
                if count > 0:
                    model.objects.all().delete()
                    self.log_warning(f"Eliminados {count} registros de {model.__name__}")
            except Exception as e:
                self.log_error(f"Error limpiando {model.__name__}: {str(e)}")
    
    def validate_dependencies(self, dependencies):
        """
        Validar que las dependencias existen antes de poblar
        """
        for model, field, value in dependencies:
            try:
                if not model.objects.filter(**{field: value}).exists():
                    self.log_error(f"Dependencia faltante: {model.__name__}.{field}={value}")
                    return False
            except Exception as e:
                self.log_error(f"Error validando dependencia {model.__name__}: {str(e)}")
                return False
        return True
    
    def handle(self, *args, **options):
        """
        Método principal - debe ser sobrescrito por las clases hijas
        """
        raise NotImplementedError("Las clases hijas deben implementar handle()")
