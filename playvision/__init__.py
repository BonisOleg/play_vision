# Load Celery app when Django starts
# Temporarily commented until celery is installed
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    # Celery not installed yet
    pass

