from django.contrib import admin
from .models import (
    NotificationTemplate, 
    PushSubscription, 
    Notification,
    NotificationPreference, 
    EmailCampaign, 
    NotificationLog,
    NewsletterSubscriber
)


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'status', 'source', 'subscribed_at', 'emails_sent']
    list_filter = ['status', 'source', 'subscribed_at']
    search_fields = ['email', 'name']
    readonly_fields = ['subscribed_at', 'unsubscribed_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'email', 'user', 'status', 'source')
        }),
        ('Статистика', {
            'fields': ('emails_sent', 'emails_opened', 'emails_clicked', 'last_sent_at')
        }),
        ('Технічні дані', {
            'fields': ('ip_address', 'user_agent', 'subscribed_at', 'unsubscribed_at')
        }),
        ('Метадані', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'notification_type', 'channel', 'is_active']
    list_filter = ['notification_type', 'channel', 'is_active']
    search_fields = ['name', 'subject_template']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'status', 'scheduled_at', 'sent_at']
    list_filter = ['status', 'template__notification_type']
    search_fields = ['user__email', 'subject']
    date_hierarchy = 'created_at'
