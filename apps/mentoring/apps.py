from django.apps import AppConfig


class MentoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.mentoring'
    verbose_name = 'Mentoring & Coaching'
    
    def ready(self):
        """Import signals when app is ready"""
        try:
            import apps.mentoring.signals  # noqa F401
        except ImportError:
            pass