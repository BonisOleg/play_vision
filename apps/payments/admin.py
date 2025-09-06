from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Payment, Order, OrderItem, Coupon, CouponUsage, WebhookEvent


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'amount', 'currency', 'status', 'payment_type',
        'stripe_payment_intent_id', 'created_at'
    ]
    list_filter = [
        'status', 'payment_type', 'currency', 'created_at'
    ]
    search_fields = [
        'user__email', 'stripe_payment_intent_id', 'description'
    ]
    readonly_fields = [
        'stripe_payment_intent_id', 'client_secret', 'provider_response',
        'created_at', 'updated_at', 'completed_at'
    ]
    
    fieldsets = (
        ('Основна інформація', {
            'fields': (
                'user', 'amount', 'currency', 'status', 'payment_type'
            )
        }),
        ('Stripe дані', {
            'fields': (
                'stripe_payment_intent_id', 'payment_method', 'requires_3ds',
                'client_secret'
            )
        }),
        ('Додатково', {
            'fields': ('description', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Відповідь провайдера', {
            'fields': ('provider_response',),
            'classes': ('collapse',)
        }),
        ('Часові мітки', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ['total']
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'status', 'total', 'payment_link',
        'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__email']
    readonly_fields = [
        'order_number', 'subtotal', 'discount_amount', 'tax_amount',
        'total', 'created_at', 'updated_at', 'completed_at'
    ]
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('user', 'order_number', 'status')
        }),
        ('Ціни', {
            'fields': (
                'subtotal', 'discount_amount', 'tax_amount', 'total'
            )
        }),
        ('Знижки', {
            'fields': ('coupon',)
        }),
        ('Платіж', {
            'fields': ('payment',)
        }),
        ('Часові мітки', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        })
    )
    
    def payment_link(self, obj):
        if obj.payment:
            url = reverse('admin:payments_payment_change', args=[obj.payment.id])
            return format_html('<a href="{}">Платіж #{}</a>', url, obj.payment.id)
        return "—"
    payment_link.short_description = "Платіж"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'payment', 'coupon')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'discount_display', 'used_count', 'max_uses',
        'valid_from', 'valid_until', 'is_active'
    ]
    list_filter = [
        'discount_type', 'is_active', 'once_per_user', 'valid_from', 'valid_until'
    ]
    search_fields = ['code', 'description']
    readonly_fields = ['used_count']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('code', 'description', 'is_active')
        }),
        ('Знижка', {
            'fields': ('discount_type', 'discount_value')
        }),
        ('Обмеження', {
            'fields': (
                'min_amount', 'max_uses', 'used_count', 'once_per_user'
            )
        }),
        ('Період дії', {
            'fields': ('valid_from', 'valid_until')
        })
    )
    
    def discount_display(self, obj):
        return obj.get_discount_display()
    discount_display.short_description = "Знижка"
    
    def save_model(self, request, obj, form, change):
        # Convert code to uppercase
        obj.code = obj.code.upper()
        super().save_model(request, obj, form, change)


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ['coupon', 'user', 'order', 'used_at']
    list_filter = ['used_at']
    search_fields = ['coupon__code', 'user__email', 'order__order_number']
    readonly_fields = ['used_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('coupon', 'user', 'order')


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = [
        'event_id', 'event_type', 'processed', 'created_at', 'processed_at'
    ]
    list_filter = ['event_type', 'processed', 'created_at']
    search_fields = ['event_id', 'event_type']
    readonly_fields = [
        'event_id', 'event_type', 'payload', 'created_at', 'processed_at'
    ]
    
    fieldsets = (
        ('Webhook інформація', {
            'fields': ('event_id', 'event_type', 'processed')
        }),
        ('Обробка', {
            'fields': ('error', 'created_at', 'processed_at')
        }),
        ('Дані', {
            'fields': ('payload',),
            'classes': ('collapse',)
        })
    )
    
    def has_add_permission(self, request):
        return False  # Webhooks are created automatically
    
    def has_delete_permission(self, request, obj=None):
        return False  # Keep webhook history