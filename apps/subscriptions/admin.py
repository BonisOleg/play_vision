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
    
    search_fields = ['name', 'badge_text', 'feature_1_monthly', 'feature_2_monthly', 'feature_3_monthly']
    
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
        ('Базова ціна', {
            'fields': (
                ('base_price_uah', 'base_price_usd'),
            ),
            'description': 'Базова ціна за місяць'
        }),
        ('Знижки без таймера', {
            'fields': (
                ('discount_monthly', 'discount_3_months'),
            ),
            'description': 'Звичайні знижки без таймера. Застосовуються якщо таймер не активний.'
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
        """Попередній перегляд цін в гривнях з відображенням знижок"""
        from decimal import Decimal
        
        # Місячна підписка
        base_monthly = obj.base_price_uah
        final_monthly = obj.calculate_price('monthly', 'uah')
        discount_monthly = obj.get_active_discount('monthly')
        
        if discount_monthly > 0:
            old_price = f'<span style="text-decoration: line-through; color: #999;">{base_monthly:.0f} грн</span>'
            new_price = f'<span style="color: #e11d48; font-weight: bold;">{final_monthly:.0f} грн</span>'
            discount_amount = base_monthly - final_monthly
            monthly = f"{old_price} → {new_price} /міс<br><small style='color: #10b981;'>Економія: {discount_amount:.0f} грн ({discount_monthly}%)</small>"
        else:
            monthly = f"{base_monthly:.0f} грн/міс"
        
        # 3-місячна підписка
        base_3m = obj.base_price_uah * 3
        final_3m = obj.calculate_price('3_months', 'uah')
        discount_3m = obj.get_active_discount('3_months')
        monthly_3m = final_3m / 3
        
        if discount_3m > 0:
            old_price = f'<span style="text-decoration: line-through; color: #999;">{base_3m:.0f} грн</span>'
            new_price = f'<span style="color: #e11d48; font-weight: bold;">{final_3m:.0f} грн</span>'
            discount_amount = base_3m - final_3m
            three_months = f"{old_price} → {new_price} за 3міс<br><small style='color: #10b981;'>Економія: {discount_amount:.0f} грн ({discount_3m}%) | {monthly_3m:.0f} грн/міс</small>"
        else:
            three_months = f"{base_3m:.0f} грн за 3міс ({obj.base_price_uah:.0f} грн/міс)"
        
        return format_html(
            '<div style="line-height: 1.8;">'
            '<strong>Місяць:</strong><br>{}<br><br>'
            '<strong>3 міс:</strong><br>{}'
            '</div>',
            monthly, three_months
        )
    price_preview_uah.short_description = 'Ціни (₴)'
    
    def price_preview_usd(self, obj):
        """Попередній перегляд цін в доларах з відображенням знижок"""
        from decimal import Decimal
        
        # Місячна підписка
        base_monthly = obj.base_price_usd
        final_monthly = obj.calculate_price('monthly', 'usd')
        discount_monthly = obj.get_active_discount('monthly')
        
        if discount_monthly > 0:
            old_price = f'<span style="text-decoration: line-through; color: #999;">${base_monthly:.0f}</span>'
            new_price = f'<span style="color: #e11d48; font-weight: bold;">${final_monthly:.0f}</span>'
            discount_amount = base_monthly - final_monthly
            monthly = f"{old_price} → {new_price} /міс<br><small style='color: #10b981;'>Економія: ${discount_amount:.0f} ({discount_monthly}%)</small>"
        else:
            monthly = f"${base_monthly:.0f}/міс"
        
        # 3-місячна підписка
        base_3m = obj.base_price_usd * 3
        final_3m = obj.calculate_price('3_months', 'usd')
        discount_3m = obj.get_active_discount('3_months')
        monthly_3m = final_3m / 3
        
        if discount_3m > 0:
            old_price = f'<span style="text-decoration: line-through; color: #999;">${base_3m:.0f}</span>'
            new_price = f'<span style="color: #e11d48; font-weight: bold;">${final_3m:.0f}</span>'
            discount_amount = base_3m - final_3m
            three_months = f"{old_price} → {new_price} за 3міс<br><small style='color: #10b981;'>Економія: ${discount_amount:.0f} ({discount_3m}%) | ${monthly_3m:.0f}/міс</small>"
        else:
            three_months = f"${base_3m:.0f} за 3міс (${obj.base_price_usd:.0f}/міс)"
        
        return format_html(
            '<div style="line-height: 1.8;">'
            '<strong>Місяць:</strong><br>{}<br><br>'
            '<strong>3 міс:</strong><br>{}'
            '</div>',
            monthly, three_months
        )
    price_preview_usd.short_description = 'Ціни ($)'
    
    def periods_available(self, obj):
        """Показує доступні періоди"""
        periods = []
        if obj.available_monthly:
            periods.append('1 міс')
        if obj.available_3_months:
            periods.append('3 міс')
        
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

