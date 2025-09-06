from django.apps import AppConfig


class LoyaltyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.loyalty'
    verbose_name = 'Loyalty Program'
    
    def ready(self):
        """Import signals when app is ready"""
        try:
            import apps.loyalty.signals  # noqa F401
        except ImportError:
            pass