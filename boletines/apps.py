from django.apps import AppConfig


class BoletinesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'boletines'
    
    def ready(self):
        import boletines.signals
