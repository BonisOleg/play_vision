from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    Event, Speaker, EventTicket, EventRegistration, 
    EventWaitlist, EventFeedback
)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Події 🧪 BETA"""
    list_display = [
        'title', 'event_type', 'event_category', 'start_datetime', 'status', 
        'tickets_sold', 'max_attendees', 'is_featured'
    ]
    list_filter = [
        'event_type', 'event_category', 'status', 'is_featured', 'requires_subscription',
        'is_free', 'start_datetime'
    ]
    search_fields = ['title', 'description', 'location']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['speakers']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': (
                'title', 'slug', 'description', 'short_description',
                'event_type', 'event_category', 'status'
            )
        }),
        ('Дата та локація', {
            'fields': (
                'start_datetime', 'end_datetime', 'timezone_name',
                'location', 'online_link'
            )
        }),
        ('Квитки та ціни', {
            'fields': (
                'max_attendees', 'price', 'is_free', 
                'requires_subscription'
            )
        }),
        ('Організація', {
            'fields': (
                'organizer', 'speakers'
            )
        }),
        ('Медіа', {
            'fields': ('thumbnail', 'banner_image')
        }),
        ('Налаштування', {
            'fields': (
                'is_featured', 'requires_approval', 'send_reminders'
            ),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['tickets_sold']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('organizer')


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'email', 'position', 'company', 
        'is_active', 'is_featured'
    ]
    list_filter = ['is_active', 'is_featured', 'company']
    search_fields = ['first_name', 'last_name', 'email', 'company']
    
    fieldsets = (
        ('Особиста інформація', {
            'fields': ('first_name', 'last_name', 'email', 'photo')
        }),
        ('Професійна інформація', {
            'fields': ('position', 'company', 'bio')
        }),
        ('Соціальні мережі', {
            'fields': ('linkedin_url', 'twitter_url', 'website_url'),
            'classes': ('collapse',)
        }),
        ('Налаштування', {
            'fields': ('is_active', 'is_featured')
        })
    )


@admin.register(EventTicket)
class EventTicketAdmin(admin.ModelAdmin):
    list_display = [
        'ticket_number', 'event', 'user', 'status', 
        'used_balance', 'created_at'
    ]
    list_filter = [
        'status', 'used_balance', 'event__event_type', 
        'created_at'
    ]
    search_fields = [
        'ticket_number', 'user__email', 'event__title'
    ]
    readonly_fields = [
        'ticket_number', 'qr_code_preview', 'used_at', 
        'checked_in_by'
    ]
    
    fieldsets = (
        ('Основна інформація', {
            'fields': (
                'event', 'user', 'ticket_number', 'status'
            )
        }),
        ('Оплата', {
            'fields': ('payment', 'used_balance')
        }),
        ('QR код', {
            'fields': ('qr_code_preview', 'qr_data'),
            'classes': ('collapse',)
        }),
        ('Використання', {
            'fields': ('used_at', 'checked_in_by')
        })
    )
    
    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" width="200" height="200" />',
                obj.qr_code.url
            )
        return "QR код не згенерований"
    qr_code_preview.short_description = "QR код"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'event', 'user', 'payment'
        )


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = [
        'ticket', 'dietary_requirements_short', 'marketing_consent',
        'created_at'
    ]
    list_filter = ['marketing_consent', 'created_at']
    search_fields = [
        'ticket__user__email', 'ticket__event__title',
        'emergency_contact'
    ]
    
    fieldsets = (
        ('Квиток', {
            'fields': ('ticket',)
        }),
        ('Додаткова інформація', {
            'fields': (
                'dietary_requirements', 'special_needs'
            )
        }),
        ('Екстрений контакт', {
            'fields': ('emergency_contact', 'emergency_phone')
        }),
        ('Маркетинг', {
            'fields': ('how_did_you_hear', 'marketing_consent')
        }),
        ('Додаткові поля', {
            'fields': ('custom_fields',),
            'classes': ('collapse',)
        })
    )
    
    def dietary_requirements_short(self, obj):
        if obj.dietary_requirements:
            return obj.dietary_requirements[:50] + "..." if len(obj.dietary_requirements) > 50 else obj.dietary_requirements
        return "—"
    dietary_requirements_short.short_description = "Дієта"


@admin.register(EventWaitlist)
class EventWaitlistAdmin(admin.ModelAdmin):
    list_display = [
        'event', 'user', 'email', 'notified', 'created_at'
    ]
    list_filter = ['notified', 'event__event_type', 'created_at']
    search_fields = ['user__email', 'email', 'event__title']
    readonly_fields = ['notified_at']
    
    actions = ['notify_waitlist']
    
    def notify_waitlist(self, request, queryset):
        # Логіка для сповіщення користувачів з листа очікування
        for waitlist_entry in queryset.filter(notified=False):
            # Тут буде логіка відправки email
            waitlist_entry.notified = True
            waitlist_entry.notified_at = timezone.now()
            waitlist_entry.save()
        
        self.message_user(
            request, 
            f"Сповіщено {queryset.count()} користувачів з листа очікування"
        )
    notify_waitlist.short_description = "Сповістити обраних з листа очікування"


@admin.register(EventFeedback)
class EventFeedbackAdmin(admin.ModelAdmin):
    list_display = [
        'event', 'user', 'overall_rating', 'would_recommend',
        'created_at'
    ]
    list_filter = [
        'overall_rating', 'would_recommend', 'would_attend_again',
        'event__event_type', 'created_at'
    ]
    search_fields = ['user__email', 'event__title']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('event', 'user')
        }),
        ('Оцінки', {
            'fields': (
                'overall_rating', 'content_rating', 
                'speaker_rating', 'organization_rating'
            )
        }),
        ('Коментарі', {
            'fields': (
                'what_liked', 'what_could_improve', 
                'additional_comments'
            )
        }),
        ('Рекомендації', {
            'fields': ('would_recommend', 'would_attend_again')
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('event', 'user')
