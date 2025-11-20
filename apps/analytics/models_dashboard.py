from django.db import models
from django.utils import timezone


class DashboardStats(models.Model):
    """
    Статистика для dashboard (автоматично оновлюється щоденно)
    """
    # Користувачі
    total_users = models.PositiveIntegerField(default=0, verbose_name='Всього користувачів')
    new_users_today = models.PositiveIntegerField(default=0, verbose_name='Нові користувачі сьогодні')
    new_users_week = models.PositiveIntegerField(default=0, verbose_name='Нові користувачі за тиждень')
    active_users_week = models.PositiveIntegerField(default=0, verbose_name='Активні користувачі за тиждень')
    
    # Час на сайті
    avg_time_on_site = models.FloatField(default=0.0, verbose_name='Середній час на сайті (хв)')
    
    # Платежі
    payments_today = models.PositiveIntegerField(default=0, verbose_name='Платежі сьогодні')
    payments_week = models.PositiveIntegerField(default=0, verbose_name='Платежі за тиждень')
    payments_month = models.PositiveIntegerField(default=0, verbose_name='Платежі за місяць')
    
    # Дохід
    revenue_today = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Дохід сьогодні')
    revenue_week = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Дохід за тиждень')
    revenue_month = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Дохід за місяць')
    
    # Метадані
    date = models.DateField(default=timezone.now, unique=True, verbose_name='Дата')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dashboard_stats'
        verbose_name = 'Статистика'
        verbose_name_plural = '📈 Статистика → Dashboard'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['-date']),
        ]
    
    def __str__(self):
        return f"Статистика {self.date}"
