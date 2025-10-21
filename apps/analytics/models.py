from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class UserSession(models.Model):
    """
    Сесії користувачів для аналітики
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                           related_name='analytics_sessions', null=True, blank=True)
    session_id = models.CharField(max_length=100, help_text='Session ID для анонімних користувачів')
    
    # Інформація про пристрій
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_type = models.CharField(max_length=20, choices=[
        ('desktop', 'Desktop'),
        ('mobile', 'Mobile'),
        ('tablet', 'Tablet'),
    ], blank=True)
    browser = models.CharField(max_length=50, blank=True)
    os = models.CharField(max_length=50, blank=True)
    
    # Геолокація
    country = models.CharField(max_length=2, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Час сесії
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    
    # Джерело трафіку
    referrer = models.URLField(blank=True)
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'analytics_sessions'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        indexes = [
            models.Index(fields=['user', 'started_at']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        user_info = self.user.email if self.user else f"Anonymous {self.session_id}"
        return f"{user_info} - {self.started_at}"


class PageView(models.Model):
    """
    Перегляди сторінок
    """
    session = models.ForeignKey(UserSession, on_delete=models.CASCADE, related_name='page_views')
    
    # Сторінка
    path = models.CharField(max_length=500)
    title = models.CharField(max_length=200, blank=True)
    
    # Час на сторінці
    viewed_at = models.DateTimeField(auto_now_add=True)
    time_on_page_seconds = models.PositiveIntegerField(default=0)
    
    # Прокрутка
    max_scroll_percentage = models.PositiveIntegerField(default=0)
    
    # Похідні дії
    had_interaction = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'analytics_page_views'
        verbose_name = 'Page View'
        verbose_name_plural = 'Page Views'
        indexes = [
            models.Index(fields=['session', 'viewed_at']),
            models.Index(fields=['path']),
        ]
    
    def __str__(self):
        return f"{self.session} - {self.path}"


class Event(models.Model):
    """
    Кастомні події для аналітики
    """
    EVENT_CATEGORIES = [
        ('engagement', 'Взаємодія'),
        ('conversion', 'Конверсія'),
        ('content', 'Контент'),
        ('commerce', 'Комерція'),
        ('social', 'Соціальна активність'),
    ]
    
    session = models.ForeignKey(UserSession, on_delete=models.CASCADE, related_name='events')
    
    # Подія
    event_name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=EVENT_CATEGORIES)
    action = models.CharField(max_length=100)
    label = models.CharField(max_length=200, blank=True)
    value = models.FloatField(null=True, blank=True)
    
    # Контекст
    page_path = models.CharField(max_length=500, blank=True)
    properties = models.JSONField(default=dict, help_text='Додаткові властивості події')
    
    # Час
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytics_events'
        verbose_name = 'Analytics Event'
        verbose_name_plural = 'Analytics Events'
        indexes = [
            models.Index(fields=['session', 'timestamp']),
            models.Index(fields=['event_name', 'category']),
        ]
    
    def __str__(self):
        return f"{self.event_name} - {self.action}"


class ConversionFunnel(models.Model):
    """
    Воронки конверсії
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    steps = models.JSONField(help_text='Кроки воронки з умовами')
    is_active = models.BooleanField(default=True)
    
    # Метадані
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytics_funnels'
        verbose_name = 'Conversion Funnel'
        verbose_name_plural = 'Conversion Funnels'
    
    def __str__(self):
        return self.name


class FunnelStep(models.Model):
    """
    Проходження кроків воронки користувачами
    """
    funnel = models.ForeignKey(ConversionFunnel, on_delete=models.CASCADE, related_name='completions')
    session = models.ForeignKey(UserSession, on_delete=models.CASCADE, related_name='funnel_steps')
    step_number = models.PositiveIntegerField()
    step_name = models.CharField(max_length=100)
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytics_funnel_steps'
        verbose_name = 'Funnel Step'
        verbose_name_plural = 'Funnel Steps'
        unique_together = ['funnel', 'session', 'step_number']
    
    def __str__(self):
        return f"{self.funnel.name} - Step {self.step_number}"


class ContentAnalytics(models.Model):
    """
    Аналітика контенту
    """
    # Пов'язаний контент
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Метрики
    view_count = models.PositiveIntegerField(default=0)
    unique_views = models.PositiveIntegerField(default=0)
    avg_time_spent = models.PositiveIntegerField(default=0, help_text='Середній час у секундах')
    completion_rate = models.FloatField(default=0, help_text='Відсоток завершення')
    
    # Взаємодія
    likes = models.PositiveIntegerField(default=0)
    shares = models.PositiveIntegerField(default=0)
    comments = models.PositiveIntegerField(default=0)
    bookmarks = models.PositiveIntegerField(default=0)
    
    # Конверсії
    conversions = models.PositiveIntegerField(default=0)
    conversion_rate = models.FloatField(default=0)
    
    # Дата
    date = models.DateField(default=timezone.now)
    
    class Meta:
        db_table = 'analytics_content'
        verbose_name = 'Content Analytics'
        verbose_name_plural = 'Content Analytics'
        unique_together = ['content_type', 'object_id', 'date']
        indexes = [
            models.Index(fields=['date', 'view_count']),
        ]
    
    def __str__(self):
        return f"{self.content_object} - {self.date}"


class RevenueAnalytics(models.Model):
    """
    Аналітика доходів
    """
    REVENUE_TYPES = [
        ('subscription', 'Підписка'),
        ('course', 'Курс'),
        ('event', 'Івент'),
        ('mentoring', 'Ментор-коучинг'),
    ]
    
    date = models.DateField()
    revenue_type = models.CharField(max_length=20, choices=REVENUE_TYPES)
    
    # Доходи
    gross_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    refunds = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Кількість
    transactions = models.PositiveIntegerField(default=0)
    unique_customers = models.PositiveIntegerField(default=0)
    
    # Середні показники
    avg_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        db_table = 'analytics_revenue'
        verbose_name = 'Revenue Analytics'
        verbose_name_plural = 'Revenue Analytics'
        unique_together = ['date', 'revenue_type']
    
    def __str__(self):
        return f"{self.revenue_type} - {self.date} - {self.gross_revenue}"


class UserBehaviorMetrics(models.Model):
    """
    Метрики поведінки користувачів
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                           related_name='behavior_metrics')
    date = models.DateField()
    
    # Активність
    sessions_count = models.PositiveIntegerField(default=0)
    total_time_minutes = models.PositiveIntegerField(default=0)
    pages_viewed = models.PositiveIntegerField(default=0)
    
    # Контент
    courses_viewed = models.PositiveIntegerField(default=0)
    courses_started = models.PositiveIntegerField(default=0)
    courses_completed = models.PositiveIntegerField(default=0)
    
    # Взаємодія
    events_attended = models.PositiveIntegerField(default=0)
    mentoring_sessions = models.PositiveIntegerField(default=0)
    
    # Комерція
    purchases_made = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        db_table = 'analytics_user_behavior'
        verbose_name = 'User Behavior Metrics'
        verbose_name_plural = 'User Behavior Metrics'
        unique_together = ['user', 'date']
    
    def __str__(self):
        return f"{self.user.email} - {self.date}"