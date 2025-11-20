from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta
from .models_dashboard import DashboardStats


@admin.register(DashboardStats)
class DashboardStatsAdmin(admin.ModelAdmin):
    """Admin для статистики з фільтрами по періоду"""
    
    list_display = [
        'date', 'total_users', 'new_users_week', 'active_users_week',
        'avg_time_on_site_display', 'payments_week', 'revenue_week_display'
    ]
    list_filter = ['date']
    readonly_fields = [
        'date', 'total_users', 'new_users_today', 'new_users_week', 'active_users_week',
        'avg_time_on_site', 'payments_today', 'payments_week', 'payments_month',
        'revenue_today', 'revenue_week', 'revenue_month', 'updated_at'
    ]
    
    fieldsets = (
        ('Користувачі', {
            'fields': ('total_users', 'new_users_today', 'new_users_week', 'active_users_week'),
            'description': 'Статистика користувачів'
        }),
        ('Активність', {
            'fields': ('avg_time_on_site',),
            'description': 'Середній час на сайті в хвилинах'
        }),
        ('Платежі', {
            'fields': ('payments_today', 'payments_week', 'payments_month'),
            'description': 'Кількість платежів'
        }),
        ('Дохід', {
            'fields': ('revenue_today', 'revenue_week', 'revenue_month'),
            'description': 'Дохід в грн'
        }),
        ('Метадані', {
            'fields': ('date', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def avg_time_on_site_display(self, obj):
        return f"{obj.avg_time_on_site:.1f} хв"
    avg_time_on_site_display.short_description = 'Час на сайті'
    
    def revenue_week_display(self, obj):
        return f"{obj.revenue_week:.2f} грн"
    revenue_week_display.short_description = 'Дохід за тиждень'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def changelist_view(self, request, extra_context=None):
        """Додати статистику в extra_context"""
        extra_context = extra_context or {}
        
        # Отримати статистику за останній тиждень (за замовчуванням)
        week_ago = timezone.now().date() - timedelta(days=7)
        recent_stats = DashboardStats.objects.filter(date__gte=week_ago).order_by('-date')
        
        if recent_stats.exists():
            # Агрегована статистика
            extra_context['week_stats'] = {
                'total_users': recent_stats.latest('date').total_users,
                'new_users': sum(s.new_users_today for s in recent_stats),
                'total_payments': sum(s.payments_today for s in recent_stats),
                'total_revenue': sum(s.revenue_today for s in recent_stats),
                'avg_time': recent_stats.aggregate(Avg('avg_time_on_site'))['avg_time_on_site__avg'] or 0,
            }
        
        return super().changelist_view(request, extra_context)
