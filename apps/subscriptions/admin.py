"""
Адміністрування тарифних планів та підписок користувачів
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import SubscriptionPlan, Subscription


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
        'discount_timer_monthly',
        'discount_timer_3months',
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
        ('Переваги для місячної підписки', {
            'fields': (
                'feature_1_monthly', 'feature_2_monthly', 'feature_3_monthly', 'feature_4_monthly', 'feature_5_monthly',
                'feature_6_monthly', 'feature_7_monthly', 'feature_8_monthly', 'feature_9_monthly', 'feature_10_monthly',
                'feature_11_monthly', 'feature_12_monthly', 'feature_13_monthly', 'feature_14_monthly', 'feature_15_monthly',
                'feature_16_monthly', 'feature_17_monthly', 'feature_18_monthly', 'feature_19_monthly', 'feature_20_monthly',
                'feature_21_monthly', 'feature_22_monthly', 'feature_23_monthly', 'feature_24_monthly', 'feature_25_monthly',
                'feature_26_monthly', 'feature_27_monthly', 'feature_28_monthly', 'feature_29_monthly', 'feature_30_monthly',
            ),
            'description': 'Переваги для місячної підписки. На сторінці відображаються тільки заповнені переваги.'
        }),
        ('Переваги для 3-місячної підписки', {
            'fields': (
                'feature_1_3months', 'feature_2_3months', 'feature_3_3months', 'feature_4_3months', 'feature_5_3months',
                'feature_6_3months', 'feature_7_3months', 'feature_8_3months', 'feature_9_3months', 'feature_10_3months',
                'feature_11_3months', 'feature_12_3months', 'feature_13_3months', 'feature_14_3months', 'feature_15_3months',
                'feature_16_3months', 'feature_17_3months', 'feature_18_3months', 'feature_19_3months', 'feature_20_3months',
                'feature_21_3months', 'feature_22_3months', 'feature_23_3months', 'feature_24_3months', 'feature_25_3months',
                'feature_26_3months', 'feature_27_3months', 'feature_28_3months', 'feature_29_3months', 'feature_30_3months',
            ),
            'description': 'Переваги для 3-місячної підписки. На сторінці відображаються тільки заповнені переваги.'
        }),
        ('Переваги (старі - для backward compatibility)', {
            'fields': (
                'feature_1', 'feature_2', 'feature_3', 'feature_4', 'feature_5',
                'feature_6', 'feature_7', 'feature_8', 'feature_9', 'feature_10',
                'feature_11', 'feature_12', 'feature_13', 'feature_14', 'feature_15',
                'feature_16', 'feature_17', 'feature_18', 'feature_19', 'feature_20',
                'feature_21', 'feature_22', 'feature_23', 'feature_24', 'feature_25',
                'feature_26', 'feature_27', 'feature_28', 'feature_29', 'feature_30',
            ),
            'description': 'Старі переваги (будуть видалені після міграції). Використовуються як fallback якщо нові не заповнені.',
            'classes': ('collapse',),
        }),
        ('Ціноутворення', {
            'fields': (
                ('base_price_uah', 'base_price_usd'),
                ('discount_3_months', 'discount_12_months'),
            ),
            'description': 'Базова ціна за місяць + знижки у відсотках (старі поля)'
        }),
        ('Знижки з таймерами', {
            'fields': (
                ('discount_monthly_percentage', 'discount_monthly_start_date', 'discount_monthly_end_date'),
                ('discount_3months_percentage', 'discount_3months_start_date', 'discount_3months_end_date'),
            ),
            'description': 'Знижки з таймерами. Автоматично застосовуються якщо поточна дата між start_date та end_date.'
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
    
    def discount_timer_monthly(self, obj):
        """Показує таймер знижки для monthly"""
        if not obj.discount_monthly_start_date or not obj.discount_monthly_end_date:
            return format_html('<span style="color: gray;">Не налаштовано</span>')
        
        now = timezone.now()
        if now < obj.discount_monthly_start_date:
            time_left = obj.discount_monthly_start_date - now
            return format_html(
                '<span style="color: orange;">Починається через: {} днів</span>',
                time_left.days
            )
        elif now <= obj.discount_monthly_end_date:
            time_left = obj.discount_monthly_end_date - now
            days = time_left.days
            hours = time_left.seconds // 3600
            minutes = (time_left.seconds % 3600) // 60
            return format_html(
                '<span style="color: green; font-weight: bold;">Активна! Залишилось: {}д {}г {}х ({})</span>',
                days, hours, minutes, obj.discount_monthly_percentage
            )
        else:
            return format_html('<span style="color: red;">Закінчилась</span>')
    discount_timer_monthly.short_description = 'Таймер знижки (місяць)'
    
    def discount_timer_3months(self, obj):
        """Показує таймер знижки для 3_months"""
        if not obj.discount_3months_start_date or not obj.discount_3months_end_date:
            return format_html('<span style="color: gray;">Не налаштовано</span>')
        
        now = timezone.now()
        if now < obj.discount_3months_start_date:
            time_left = obj.discount_3months_start_date - now
            return format_html(
                '<span style="color: orange;">Починається через: {} днів</span>',
                time_left.days
            )
        elif now <= obj.discount_3months_end_date:
            time_left = obj.discount_3months_end_date - now
            days = time_left.days
            hours = time_left.seconds // 3600
            minutes = (time_left.seconds % 3600) // 60
            return format_html(
                '<span style="color: green; font-weight: bold;">Активна! Залишилось: {}д {}г {}х ({})</span>',
                days, hours, minutes, obj.discount_3months_percentage
            )
        else:
            return format_html('<span style="color: red;">Закінчилась</span>')
    discount_timer_3months.short_description = 'Таймер знижки (3 міс)'
    
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


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Адмін панель для керування підписками користувачів
    """
    
    list_display = [
        'id',
        'user_email',
        'plan_name',
        'start_date',
        'end_date',
        'status_display',
        'days_left',
        'auto_renew',
        'created_at'
    ]
    
    list_filter = [
        'is_active',
        'auto_renew',
        'plan',
        'created_at',
        'end_date'
    ]
    
    search_fields = [
        'user__email',
        'user__username',
        'user__first_name',
        'user__last_name',
        'plan__name'
    ]
    
    date_hierarchy = 'created_at'
    
    readonly_fields = ['created_at', 'updated_at', 'is_expired_display']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('user', 'plan')
        }),
        ('Період дії', {
            'fields': ('start_date', 'end_date', 'is_expired_display')
        }),
        ('Налаштування', {
            'fields': ('is_active', 'auto_renew')
        }),
        ('Службова інформація', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    raw_id_fields = ['user']
    
    def user_email(self, obj):
        """Email користувача"""
        return obj.user.email
    user_email.short_description = 'Email користувача'
    user_email.admin_order_field = 'user__email'
    
    def plan_name(self, obj):
        """Назва тарифу"""
        return obj.plan.name
    plan_name.short_description = 'Тариф'
    plan_name.admin_order_field = 'plan__name'
    
    def status_display(self, obj):
        """Статус підписки з кольором"""
        now = timezone.now()
        
        if not obj.is_active:
            return format_html(
                '<span style="color: gray; font-weight: bold;">⭘ Неактивна</span>'
            )
        elif now > obj.end_date:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Закінчилась</span>'
            )
        elif now + timezone.timedelta(days=7) > obj.end_date:
            return format_html(
                '<span style="color: orange; font-weight: bold;">⚠ Закінчується</span>'
            )
        else:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Активна</span>'
            )
    status_display.short_description = 'Статус'
    
    def days_left(self, obj):
        """Скільки днів залишилось"""
        if not obj.is_active:
            return '-'
        
        now = timezone.now()
        if now > obj.end_date:
            days_ago = (now - obj.end_date).days
            return format_html('<span style="color: red;">-{} днів</span>', days_ago)
        
        days = (obj.end_date - now).days
        if days <= 7:
            color = 'orange'
        else:
            color = 'green'
        
        return format_html('<span style="color: {};">{} днів</span>', color, days)
    days_left.short_description = 'Залишилось'
    
    def is_expired_display(self, obj):
        """Чи закінчилась підписка"""
        if obj.is_expired:
            return format_html('<span style="color: red; font-weight: bold;">Так</span>')
        return format_html('<span style="color: green; font-weight: bold;">Ні</span>')
    is_expired_display.short_description = 'Закінчилась?'
    
    actions = ['deactivate_subscriptions', 'activate_subscriptions']
    
    def deactivate_subscriptions(self, request, queryset):
        """Деактивувати вибрані підписки"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'Деактивовано {count} підписок')
    deactivate_subscriptions.short_description = 'Деактивувати вибрані підписки'
    
    def activate_subscriptions(self, request, queryset):
        """Активувати вибрані підписки"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'Активовано {count} підписок')
    activate_subscriptions.short_description = 'Активувати вибрані підписки'

