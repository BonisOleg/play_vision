"""
Celery tasks for analytics
Refresh dashboard stats, cleanup old data
"""
from celery import shared_task
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def refresh_dashboard_stats(self):
    """
    Refresh dashboard statistics (runs hourly via Celery Beat)
    
    Collects metrics:
    - User counts (total, new today, active today)
    - Revenue (total, today)
    - Session duration (average, total hours)
    - Course views (top 20)
    
    Uses atomic transactions for consistency.
    """
    try:
        from .models import DashboardStats, UserSession
        from apps.accounts.models import User
        from apps.payments.models import Payment
        from apps.content.models import Course
        from django.db import transaction
        
        today = timezone.now().date()
        
        logger.info(f"Starting dashboard stats refresh for {today}")
        
        with transaction.atomic():
            stats, created = DashboardStats.objects.get_or_create(date=today)
            
            # User metrics
            stats.total_users = User.objects.count()
            stats.new_users_today = User.objects.filter(
                created_at__date=today
            ).count()
            stats.active_users_today = UserSession.objects.filter(
                started_at__date=today
            ).values('user').distinct().count()
            
            # Revenue metrics
            revenue_data = Payment.objects.filter(
                status='completed'
            ).aggregate(
                total=Sum('amount'),
                today=Sum('amount', filter=Q(completed_at__date=today))
            )
            stats.total_revenue = revenue_data['total'] or 0
            stats.revenue_today = revenue_data['today'] or 0
            
            # Session/Time metrics
            session_stats = UserSession.objects.filter(
                started_at__date=today
            ).aggregate(
                avg_duration=Avg('duration_seconds'),
                total_time=Sum('duration_seconds')
            )
            stats.avg_session_duration = int(session_stats['avg_duration'] or 0)
            stats.total_time_on_site = int(session_stats['total_time'] or 0)
            
            # Course views - top 20 courses
            course_views = dict(
                Course.objects.values_list('id', 'view_count')
                .order_by('-view_count')[:20]
            )
            stats.course_views_json = course_views
            
            stats.save()
            
        logger.info(f"Dashboard stats refreshed successfully for {today}")
        return {
            'date': str(today),
            'users': stats.total_users,
            'revenue': float(stats.total_revenue)
        }
        
    except Exception as exc:
        logger.error(f"Failed to refresh dashboard stats: {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def cleanup_old_sessions():
    """
    Cleanup old user sessions (runs daily at 2 AM)
    
    Removes sessions older than 90 days to keep database clean.
    """
    try:
        from .models import UserSession
        
        cutoff_date = timezone.now() - timedelta(days=90)
        deleted_count, _ = UserSession.objects.filter(
            started_at__lt=cutoff_date
        ).delete()
        
        logger.info(f"Cleaned up {deleted_count} old sessions")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Failed to cleanup old sessions: {e}")
        return 0


@shared_task
def aggregate_weekly_stats():
    """
    Aggregate weekly statistics for reporting
    
    Runs every Monday at 3 AM.
    """
    try:
        from .models import DashboardStats
        
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        weekly_stats = DashboardStats.objects.filter(
            date__gte=week_ago,
            date__lte=today
        ).aggregate(
            avg_users=Avg('active_users_today'),
            total_revenue=Sum('revenue_today'),
            avg_session=Avg('avg_session_duration')
        )
        
        logger.info(f"Weekly stats aggregated: {weekly_stats}")
        return weekly_stats
        
    except Exception as e:
        logger.error(f"Failed to aggregate weekly stats: {e}")
        return {}

