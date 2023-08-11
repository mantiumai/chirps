from django.apps import AppConfig


class WorkerConfig(AppConfig):
    """Worker application config"""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'worker'
