from django.apps import AppConfig


class CmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.cms'
    verbose_name = 'Content Management'
    
    def ready(self):
        """Import admin modules and signals when app is ready"""
        try:
            from . import admin_pages
        except ImportError:
            pass
        try:
            import apps.cms.signals  # noqa F401
        except ImportError:
            pass