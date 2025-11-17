"""
Admin для Dashboard статистики
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta
from .models_dashboard import DashboardStats


@admin.register(DashboardStats)
class DashboardStatsAdmin(admin.ModelAdmin):
    """Статистика з фільтрами"""
    
    list_display = [
        'date', 'total_users', 'new_users', 'payments_count', 
        'total_revenue_display', 'event_registrations', 'average_session_time'
    ]
    list_filter = ['date']
    date_hierarchy = 'date'
    readonly_fields = [
        'date', 'total_users', 'new_users', 'active_users',
        'total_courses', 'course_views', 'total_events', 'event_registrations',
        'total_revenue', 'payments_count', 'average_order',
        'total_session_time', 'average_session_time',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Дата', {
            'fields': ('date',)
        }),
        ('👥 Користувачі', {
            'fields': ('total_users', 'new_users', 'active_users')
        }),
        ('🎓 Курси', {
            'fields': ('total_courses', 'course_views')
        }),
        ('🎉 Події', {
            'fields': ('total_events', 'event_registrations')
        }),
        ('💰 Платежі', {
            'fields': ('total_revenue', 'payments_count', 'average_order')
        }),
        ('⏱ Час на сайті', {
            'fields': ('total_session_time', 'average_session_time')
        }),
        ('Метадані', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_revenue_display(self, obj):
        """Форматований дохід"""
        return format_html('<strong>{:.2f} грн</strong>', obj.total_revenue)
    total_revenue_display.short_description = 'Дохід'
    
    def has_add_permission(self, request):
        """Заборонити ручне створення - тільки через collect_stats()"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Дозволити видалення старих даних"""
        return True
    
    def changelist_view(self, request, extra_context=None):
        """Додати фільтри по періодах"""
        extra_context = extra_context or {}
        
        # Визначити період
        period = request.GET.get('period', 'week')
        today = timezone.now().date()
        
        if period == 'week':
            start_date = today - timedelta(days=7)
            extra_context['period_label'] = 'Останній тиждень'
        elif period == 'month':
            start_date = today - timedelta(days=30)
            extra_context['period_label'] = 'Останній місяць'
        elif period == 'year':
            start_date = today - timedelta(days=365)
            extra_context['period_label'] = 'Останній рік'
        else:
            start_date = today - timedelta(days=7)
            extra_context['period_label'] = 'Останній тиждень'
        
        # Фільтрувати по періоду
        stats = DashboardStats.objects.filter(date__gte=start_date, date__lte=today)
        
        # Агреговані дані
        if stats.exists():
            extra_context['period_stats'] = {
                'total_users': stats.latest('date').total_users,
                'new_users': sum([s.new_users for s in stats]),
                'total_revenue': sum([s.total_revenue for s in stats]),
                'payments_count': sum([s.payments_count for s in stats]),
                'avg_session': sum([s.average_session_time for s in stats]) / stats.count(),
            }
        
        extra_context['available_periods'] = [
            {'value': 'week', 'label': 'Тиждень'},
            {'value': 'month', 'label': 'Місяць'},
            {'value': 'year', 'label': 'Рік'},
        ]
        extra_context['selected_period'] = period
        
        return super().changelist_view(request, extra_context=extra_context)

