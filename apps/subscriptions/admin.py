"""
Адміністрування тарифних планів
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import SubscriptionPlan


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    """
    Адмін панель для керування тарифними планами
    """
    
    list_display = [
        'name',
        'display_order',
        'badge_preview',
        'price_preview_uah',
        'price_preview_usd',
        'periods_available',
        'is_popular',
        'is_active',
        'updated_at'
    ]
    
    list_editable = ['display_order', 'is_active', 'is_popular']
    
    list_filter = ['is_active', 'is_popular', 'created_at']
    
    search_fields = ['name', 'badge_text', 'feature_1', 'feature_2', 'feature_3']
    
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'slug', 'display_order', 'is_active', 'is_popular')
        }),
        ('Бейдж', {
            'fields': ('badge_text', 'badge_color'),
            'description': 'Колірна мітка над картко тарифу'
        }),
        ('Переваги (Features)', {
            'fields': (
                'feature_1',
                'feature_2',
                'feature_3',
                'feature_4',
                'feature_5'
            ),
            'description': 'Заповніть від 1 до 5 переваг тарифу. Feature_1 обов\'язкова.'
        }),
        ('Ціноутворення', {
            'fields': (
                ('base_price_uah', 'base_price_usd'),
                ('discount_3_months', 'discount_12_months'),
            ),
            'description': 'Базова ціна за місяць + знижки у відсотках'
        }),
        ('Доступні періоди', {
            'fields': (
                'available_monthly',
                'available_3_months',
                'available_12_months',
                'unavailable_text'
            ),
            'description': 'Виберіть які періоди доступні для цього тарифу'
        }),
        ('Зовнішнє посилання', {
            'fields': ('checkout_url',),
            'description': 'URL сторінки оплати на сервісі квітка'
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',),
            'description': 'Опціонально: SEO метадані для пошукових систем'
        }),
    )
    
    def badge_preview(self, obj):
        """Попередній перегляд бейджа"""
        if obj.badge_text:
            return format_html(
                '<span style="background-color: {}; color: white; padding: 4px 12px; '
                'border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
                obj.badge_color,
                obj.badge_text
            )
        return '-'
    badge_preview.short_description = 'Бейдж'
    
    def price_preview_uah(self, obj):
        """Попередній перегляд цін в гривнях"""
        monthly = f"{obj.base_price_uah} грн/міс"
        
        if obj.discount_3_months > 0:
            price_3m = obj.calculate_price('3_months', 'uah')
            monthly_3m = price_3m / 3
            three_months = f"{price_3m:.0f} грн за 3міс ({monthly_3m:.0f} грн/міс, -{obj.discount_3_months}%)"
        else:
            three_months = f"{obj.base_price_uah * 3} грн за 3міс"
        
        if obj.discount_12_months > 0:
            price_12m = obj.calculate_price('12_months', 'uah')
            monthly_12m = price_12m / 12
            twelve_months = f"{price_12m:.0f} грн за рік ({monthly_12m:.0f} грн/міс, -{obj.discount_12_months}%)"
        else:
            twelve_months = f"{obj.base_price_uah * 12} грн за рік"
        
        return format_html(
            '<div style="line-height: 1.6;">'
            '<strong>Місяць:</strong> {}<br>'
            '<strong>3 міс:</strong> {}<br>'
            '<strong>Рік:</strong> {}'
            '</div>',
            monthly, three_months, twelve_months
        )
    price_preview_uah.short_description = 'Ціни (₴)'
    
    def price_preview_usd(self, obj):
        """Попередній перегляд цін в доларах"""
        monthly = f"${obj.base_price_usd}/міс"
        
        if obj.discount_3_months > 0:
            price_3m = obj.calculate_price('3_months', 'usd')
            monthly_3m = price_3m / 3
            three_months = f"${price_3m:.0f} за 3міс (${monthly_3m:.0f}/міс)"
        else:
            three_months = f"${obj.base_price_usd * 3} за 3міс"
        
        if obj.discount_12_months > 0:
            price_12m = obj.calculate_price('12_months', 'usd')
            monthly_12m = price_12m / 12
            twelve_months = f"${price_12m:.0f} за рік (${monthly_12m:.0f}/міс)"
        else:
            twelve_months = f"${obj.base_price_usd * 12} за рік"
        
        return format_html(
            '<div style="line-height: 1.6;">'
            '{}<br>'
            '{}<br>'
            '{}'
            '</div>',
            monthly, three_months, twelve_months
        )
    price_preview_usd.short_description = 'Ціни ($)'
    
    def periods_available(self, obj):
        """Показує доступні періоди"""
        periods = []
        if obj.available_monthly:
            periods.append('1 міс')
        if obj.available_3_months:
            periods.append('3 міс')
        if obj.available_12_months:
            periods.append('12 міс')
        
        if periods:
            return format_html(
                '<span style="color: green;">✓ {}</span>',
                ', '.join(periods)
            )
        return format_html('<span style="color: red;">✗ Немає доступних періодів</span>')
    periods_available.short_description = 'Доступні періоди'
    
    def save_model(self, request, obj, form, change):
        """Зберігаємо з логуванням"""
        if change:
            # Логування змін
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f'Оновлено тариф "{obj.name}" користувачем {request.user.username}')
        
        super().save_model(request, obj, form, change)
    
    class Media:
        css = {
            'all': ('admin/css/subscription_admin.css',)
        }

