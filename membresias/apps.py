from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MembresiasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "membresias"
    verbose_name = _("Membresías")

    def ready(self):
        try:
            import membresias.signals  # noqa
        except ImportError:
            pass
