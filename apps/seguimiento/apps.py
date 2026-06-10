from django.apps import AppConfig


class SeguimientoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.seguimiento'
    verbose_name = 'Seguimiento'

    def ready(self):
        import apps.seguimiento.signals  # noqa: F401 — activa las señales
