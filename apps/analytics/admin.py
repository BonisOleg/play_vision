"""
Analytics admin
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import DashboardStats


@admin.register(DashboardStats)
class DashboardStatsAdmin(admin.ModelAdmin):
    """Admin for dashboard statistics"""
    list_display = [
        'date', 'total_users', 'new_users_today', 'revenue_today',
        'avg_session_minutes', 'active_users_today', 'updated_at'
    ]
    list_filter = ['date']
    search_fields = ['date']
    date_hierarchy = 'date'
    readonly_fields = [
        'date', 'total_users', 'new_users_today', 'active_users_today',
        'total_revenue', 'revenue_today', 'avg_session_duration',
        'total_time_on_site', 'course_views_json', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Date', {
            'fields': ('date',)
        }),
        ('User Metrics', {
            'fields': ('total_users', 'new_users_today', 'active_users_today')
        }),
        ('Revenue Metrics', {
            'fields': ('total_revenue', 'revenue_today')
        }),
        ('Session Metrics', {
            'fields': ('avg_session_duration', 'total_time_on_site')
        }),
        ('Course Views', {
            'fields': ('course_views_json',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False  # Stats are created by Celery task
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def avg_session_minutes(self, obj):
        """Display in minutes"""
        return f"{obj.avg_session_minutes:.1f}m"
    avg_session_minutes.short_description = 'Avg Session'
    avg_session_minutes.admin_order_field = 'avg_session_duration'
    
    class Media:
        css = {'all': ('admin/css/playvision-admin.css',)}
