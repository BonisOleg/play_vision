from django.contrib import admin
from .models import LoyaltyAccount, PointTransaction, PointEarningRule, RedemptionOption


@admin.register(LoyaltyAccount)
class LoyaltyAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'points', 'lifetime_points', 'lifetime_purchases', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-points']

    fieldsets = [
        ('Користувач', {
            'fields': ['user']
        }),
        ('Бали', {
            'fields': ['points', 'lifetime_points', 'lifetime_spent_points']
        }),
        ('Статистика', {
            'fields': ['lifetime_purchases']
        }),
        ('Дати', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ['account', 'points', 'transaction_type', 'reason', 'balance_after', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['account__user__email', 'reason']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

    fieldsets = [
        ('Транзакція', {
            'fields': ['account', 'points', 'transaction_type', 'reason']
        }),
        ('Посилання', {
            'fields': ['reference_type', 'reference_id'],
            'classes': ['collapse']
        }),
        ('Результат', {
            'fields': ['balance_after', 'created_at']
        }),
    ]


@admin.register(PointEarningRule)
class PointEarningRuleAdmin(admin.ModelAdmin):
    list_display = ['rule_type', 'subscription_tier', 'amount_range', 'subscription_duration_months', 'points', 'is_active', 'order']
    list_filter = ['rule_type', 'subscription_tier', 'is_active']
    ordering = ['order', 'min_amount']

    fieldsets = [
        ('Основне', {
            'fields': ['rule_type', 'subscription_tier', 'points', 'is_active', 'order']
        }),
        ('Для покупок', {
            'fields': ['min_amount', 'max_amount'],
            'classes': ['collapse'],
            'description': 'Заповнюйте тільки для правил типу "За покупку"'
        }),
        ('Для підписок', {
            'fields': ['subscription_duration_months'],
            'classes': ['collapse'],
            'description': 'Заповнюйте тільки для правил типу "За підписку"'
        }),
    ]

    def amount_range(self, obj):
        if obj.rule_type == 'purchase':
            if obj.min_amount and obj.max_amount:
                return f"₴{obj.min_amount}-{obj.max_amount}"
            elif obj.min_amount:
                return f"₴{obj.min_amount}+"
            return "-"
        return "-"
    amount_range.short_description = 'Діапазон суми'


@admin.register(RedemptionOption)
class RedemptionOptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'option_type', 'points_required', 'discount_percentage', 'subscription_tier', 'requires_subscription', 'is_active']
    list_filter = ['option_type', 'requires_subscription', 'is_active']
    ordering = ['display_order', 'points_required']

    fieldsets = [
        ('Основне', {
            'fields': ['option_type', 'name', 'description', 'points_required', 'is_active', 'display_order']
        }),
        ('Для знижок', {
            'fields': ['discount_percentage'],
            'classes': ['collapse']
        }),
        ('Для місяця підписки', {
            'fields': ['subscription_tier'],
            'classes': ['collapse']
        }),
        ('Обмеження', {
            'fields': ['requires_subscription']
        }),
    ]
