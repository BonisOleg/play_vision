from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.analytics'
    verbose_name = 'Analytics'
    
    def ready(self):
        """Import signals when app is ready"""
        try:
            import apps.analytics.signals  # noqa F401
        except ImportError:
            pass