from django.apps import AppConfig


class AiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai'
    verbose_name = 'AI Agent'
    
    def ready(self):
        """Import signals when app is ready"""
        try:
            import apps.ai.signals  # noqa F401
        except ImportError:
            pass