"""
Модель для статистики Dashboard
"""
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta


class DashboardStats(models.Model):
    """Статистика для admin dashboard"""
    
    # Дата статистики
    date = models.DateField('Дата', unique=True, db_index=True)
    
    # Користувачі
    total_users = models.IntegerField('Всього користувачів', default=0)
    new_users = models.IntegerField('Нових за день', default=0)
    active_users = models.IntegerField('Активних за день', default=0)
    
    # Курси
    total_courses = models.IntegerField('Всього курсів', default=0)
    course_views = models.IntegerField('Переглядів курсів', default=0)
    
    # Події
    total_events = models.IntegerField('Всього подій', default=0)
    event_registrations = models.IntegerField('Реєстрацій на події', default=0)
    
    # Платежі
    total_revenue = models.DecimalField('Загальний дохід (грн)', max_digits=10, decimal_places=2, default=0)
    payments_count = models.IntegerField('Кількість платежів', default=0)
    average_order = models.DecimalField('Середній чек (грн)', max_digits=10, decimal_places=2, default=0)
    
    # Час на сайті
    total_session_time = models.IntegerField('Загальний час на сайті (хв)', default=0)
    average_session_time = models.FloatField('Середній час сесії (хв)', default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytics_dashboard_stats'
        verbose_name = 'Статистика'
        verbose_name_plural = 'Статистика Dashboard'
        ordering = ['-date']
    
    def __str__(self):
        return f"Статистика за {self.date}"
    
    @classmethod
    def collect_stats(cls, date=None):
        """Зібрати статистику за дату"""
        if date is None:
            date = timezone.now().date()
        
        from apps.accounts.models import User
        from apps.content.models import Course
        from apps.events.models import Event, EventRegistration
        from apps.payments.models import Payment
        from apps.analytics.models import UserSession
        
        # Початок та кінець дня
        start = datetime.combine(date, datetime.min.time())
        end = datetime.combine(date, datetime.max.time())
        
        # Користувачі
        total_users = User.objects.count()
        new_users = User.objects.filter(date_joined__date=date).count()
        active_users = UserSession.objects.filter(
            start_time__range=(start, end)
        ).values('user').distinct().count() if UserSession.objects.exists() else 0
        
        # Курси
        total_courses = Course.objects.filter(is_published=True).count()
        # Якщо є ContentAnalytics - взяти звідти
        course_views = 0
        
        # Події
        total_events = Event.objects.count()
        event_registrations = EventRegistration.objects.filter(
            registered_at__date=date
        ).count()
        
        # Платежі
        payments = Payment.objects.filter(
            created_at__date=date,
            status='completed'
        )
        total_revenue = sum([p.amount for p in payments]) if payments.exists() else 0
        payments_count = payments.count()
        average_order = total_revenue / payments_count if payments_count > 0 else 0
        
        # Час на сайті
        sessions = UserSession.objects.filter(
            start_time__range=(start, end)
        ) if UserSession.objects.exists() else []
        
        total_session_time = 0
        for session in sessions:
            if session.end_time:
                duration = (session.end_time - session.start_time).total_seconds() / 60
                total_session_time += duration
        
        average_session_time = total_session_time / len(sessions) if sessions else 0
        
        # Зберегти
        stats, created = cls.objects.update_or_create(
            date=date,
            defaults={
                'total_users': total_users,
                'new_users': new_users,
                'active_users': active_users,
                'total_courses': total_courses,
                'course_views': course_views,
                'total_events': total_events,
                'event_registrations': event_registrations,
                'total_revenue': total_revenue,
                'payments_count': payments_count,
                'average_order': average_order,
                'total_session_time': int(total_session_time),
                'average_session_time': average_session_time,
            }
        )
        
        return stats

