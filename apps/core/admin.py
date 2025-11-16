"""
Core admin - AuditLog and ContentVersion
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import AuditLog, ContentVersion


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    View-only audit logs - immutable history
    """
    list_display = ['timestamp', 'user', 'action', 'content_type', 'object_repr', 'ip_address']
    list_filter = ['action', 'timestamp', 'content_type']
    search_fields = ['object_repr', 'user__email', 'ip_address']
    date_hierarchy = 'timestamp'
    readonly_fields = [
        'user', 'content_type', 'object_id', 'object_repr',
        'action', 'changes_display', 'timestamp', 'ip_address', 'user_agent_display'
    ]
    
    fieldsets = (
        ('Action', {
            'fields': ('action', 'timestamp', 'user', 'ip_address')
        }),
        ('Object', {
            'fields': ('content_type', 'object_id', 'object_repr')
        }),
        ('Changes', {
            'fields': ('changes_display',),
        }),
        ('Request Context', {
            'fields': ('user_agent_display',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False  # NEVER delete audit logs
    
    def changes_display(self, obj):
        """Format changes as HTML table"""
        if not obj.changes:
            return "No changes"
        
        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '<thead><tr style="background: #f0f0f0;"><th style="padding: 8px; border: 1px solid #ddd;">Field</th><th style="padding: 8px; border: 1px solid #ddd;">Old Value</th><th style="padding: 8px; border: 1px solid #ddd;">New Value</th></tr></thead>'
        html += '<tbody>'
        
        for field, change in obj.changes.items():
            old = change.get('old', '')
            new = change.get('new', '')
            html += f'<tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>{field}</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{old}</td><td style="padding: 8px; border: 1px solid #ddd; background: #e6ffe6;">{new}</td></tr>'
        
        html += '</tbody></table>'
        return format_html(html)
    changes_display.short_description = 'Changes'
    
    def user_agent_display(self, obj):
        """Display user agent in readable format"""
        if not obj.user_agent:
            return "N/A"
        return format_html('<code style="font-size: 0.9em;">{}</code>', obj.user_agent[:200])
    user_agent_display.short_description = 'User Agent'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'content_type')
    
    class Media:
        css = {'all': ('admin/css/playvision-admin.css',)}


@admin.register(ContentVersion)
class ContentVersionAdmin(admin.ModelAdmin):
    """
    Content version history
    """
    list_display = ['__str__', 'content_type', 'object_id', 'version_number', 'created_by', 'created_at']
    list_filter = ['content_type', 'created_at']
    search_fields = ['object_id', 'created_by__email', 'change_summary']
    date_hierarchy = 'created_at'
    readonly_fields = [
        'content_type', 'object_id', 'version_number',
        'snapshot_display', 'created_by', 'created_at'
    ]
    
    fieldsets = (
        ('Version Info', {
            'fields': ('content_type', 'object_id', 'version_number', 'created_by', 'created_at')
        }),
        ('Changes', {
            'fields': ('change_summary',)
        }),
        ('Snapshot', {
            'fields': ('snapshot_display',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  # Only superuser can delete versions
    
    def snapshot_display(self, obj):
        """Display snapshot as formatted JSON"""
        import json
        try:
            formatted = json.dumps(obj.snapshot, indent=2)
            return format_html('<pre style="background: #f5f5f5; padding: 1rem; border-radius: 6px; overflow-x: auto;">{}</pre>', formatted)
        except:
            return obj.snapshot
    snapshot_display.short_description = 'Snapshot Data'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by', 'content_type')
    
    class Media:
        css = {'all': ('admin/css/playvision-admin.css',)}
