"""
Celery configuration for Play Vision
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'playvision.settings.production')

app = Celery('playvision')

# Load config from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Periodic task schedule
app.conf.beat_schedule = {
    'refresh-dashboard-stats': {
        'task': 'apps.analytics.tasks.refresh_dashboard_stats',
        'schedule': crontab(minute=0),  # Every hour
    },
    'warm-content-cache': {
        'task': 'apps.cms.tasks.warm_all_caches',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    'cleanup-old-sessions': {
        'task': 'apps.analytics.tasks.cleanup_old_sessions',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
}

# Celery task configuration
app.conf.update(
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,  # One task at a time
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery"""
    print(f'Request: {self.request!r}')

