from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal


class LoyaltyTier(models.Model):
    """
    LEGACY: Система рівнів лояльності (Bronze/Silver/Gold/Platinum)
    Залишена для зворотної сумісності з існуючим кодом
    """
    name = models.CharField(max_length=50, unique=True)
    points_required = models.PositiveIntegerField(help_text='Points needed to reach this tier')
    discount_percentage = models.PositiveIntegerField(default=0, help_text='Discount percentage for this tier')
    color = models.CharField(max_length=7, default='#666666', help_text='Hex color for UI display')
    benefits = models.JSONField(default=list, help_text='List of tier benefits')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text='Display order')

    class Meta:
        db_table = 'loyalty_tiers'
        ordering = ['order', 'points_required']
        verbose_name = 'Loyalty Tier (Legacy)'
        verbose_name_plural = 'Loyalty Tiers (Legacy)'

    def __str__(self):
        return f"{self.name} ({self.points_required} points)"

    @classmethod
    def get_tier_for_points(cls, points):
        """Get appropriate tier for given points"""
        return cls.objects.filter(
            points_required__lte=points,
            is_active=True
        ).order_by('-points_required').first()


class LoyaltyAccount(models.Model):
    """
    Аккаунт користувача в програмі лояльності
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='loyalty_account'
    )
    points = models.PositiveIntegerField(default=0, help_text='Поточний баланс балів')
    lifetime_points = models.PositiveIntegerField(
        default=0,
        help_text='Всього балів зароблено за весь час'
    )
    lifetime_spent_points = models.PositiveIntegerField(
        default=0,
        help_text='Всього балів витрачено'
    )
    lifetime_purchases = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Всього витрачено грошей'
    )
    # Legacy tier support
    current_tier = models.ForeignKey(
        LoyaltyTier,
        on_delete=models.PROTECT,
        related_name='users',
        null=True,
        blank=True,
        help_text='Legacy tier (для зворотної сумісності)'
    )
    tier_achieved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'loyalty_accounts'
        verbose_name = 'Loyalty Account'
        verbose_name_plural = 'Loyalty Accounts'

    def __str__(self):
        return f"{self.user.email} - {self.points} балів"

    def add_points(self, points: int, transaction_type: str, reason: str,
                   reference_type: str = '', reference_id: int = None) -> int:
        """Нарахувати бали"""
        if points <= 0:
            return self.points

        self.points += points
        self.lifetime_points += points
        self.save(update_fields=['points', 'lifetime_points', 'updated_at'])

        PointTransaction.objects.create(
            account=self,
            points=points,
            transaction_type=transaction_type,
            reason=reason,
            reference_type=reference_type,
            reference_id=reference_id,
            balance_after=self.points
        )

        return self.points

    def spend_points(self, points: int, reason: str,
                     reference_type: str = '', reference_id: int = None) -> bool:
        """Витратити бали"""
        if points <= 0 or self.points < points:
            return False

        self.points -= points
        self.lifetime_spent_points += points
        self.save(update_fields=['points', 'lifetime_spent_points', 'updated_at'])

        PointTransaction.objects.create(
            account=self,
            points=-points,
            transaction_type='spent',
            reason=reason,
            reference_type=reference_type,
            reference_id=reference_id,
            balance_after=self.points
        )

        return True

    def get_discount_percentage(self) -> int:
        """Розрахувати знижку на основі балів (50 балів = 5%, 100 балів = 10%)"""
        if self.points >= 100:
            return 10
        elif self.points >= 50:
            return 5
        return 0


class PointTransaction(models.Model):
    """
    Історія транзакцій балів
    """
    TRANSACTION_TYPES = [
        ('purchase', 'За покупку'),
        ('subscription', 'За підписку'),
        ('spent_discount', 'Витрачено на знижку'),
        ('spent_content', 'Витрачено на контент'),
        ('spent_subscription_month', 'Обмін на місяць підписки'),
        ('bonus', 'Бонус'),
        ('expired', 'Згоріли'),
        ('adjusted', 'Коригування'),
    ]

    account = models.ForeignKey(
        LoyaltyAccount,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    points = models.IntegerField(help_text='Додатнє - нараховано, від\'ємне - витрачено')
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    reason = models.CharField(max_length=255, help_text='Опис транзакції')
    reference_type = models.CharField(max_length=50, blank=True, help_text='order, subscription, etc.')
    reference_id = models.PositiveIntegerField(null=True, blank=True)
    balance_after = models.PositiveIntegerField(help_text='Баланс після транзакції')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'point_transactions'
        verbose_name = 'Point Transaction'
        verbose_name_plural = 'Point Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['account', '-created_at']),
            models.Index(fields=['reference_type', 'reference_id']),
        ]

    def __str__(self):
        action = "+" if self.points > 0 else ""
        return f"{self.account.user.email}: {action}{self.points} балів"


class PointEarningRule(models.Model):
    """
    Правила нарахування балів згідно матриці зі скрінів
    """
    RULE_TYPES = [
        ('purchase', 'За покупку'),
        ('subscription', 'За підписку'),
    ]

    SUBSCRIPTION_TIERS = [
        ('none', 'Без підписки'),
        ('c_vision', 'C-Vision'),
        ('b_vision', 'B-Vision'),
        ('a_vision', 'A-Vision'),
        ('pro_vision', 'Pro-Vision'),
    ]

    rule_type = models.CharField(max_length=20, choices=RULE_TYPES)
    subscription_tier = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_TIERS,
        default='none',
        help_text='Рівень підписки для розрахунку'
    )

    # Для покупок: діапазон суми
    min_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        help_text='Мінімальна сума покупки (для правил "За покупку")'
    )
    max_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        help_text='Максимальна сума покупки (null = без ліміту)'
    )

    # Для підписок: термін
    subscription_duration_months = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Термін підписки в місяцях (для правил "За підписку")'
    )

    # Бали до нарахування
    points = models.PositiveIntegerField(help_text='Скільки балів нарахувати')

    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text='Порядок застосування')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'point_earning_rules'
        verbose_name = 'Point Earning Rule'
        verbose_name_plural = 'Point Earning Rules'
        ordering = ['order', 'min_amount']

    def __str__(self):
        if self.rule_type == 'purchase':
            amount_range = f"₴{self.min_amount}-{self.max_amount or '∞'}"
            return f"Покупка {amount_range} ({self.get_subscription_tier_display()}): +{self.points}"
        else:
            return f"Підписка {self.get_subscription_tier_display()} {self.subscription_duration_months}міс: +{self.points}"

    @classmethod
    def get_points_for_purchase(cls, amount: Decimal, user_subscription_tier: str = 'none') -> int:
        """
        Розрахувати бали за покупку згідно матриці:
        ₴399-1000: none=5, c/b=8, a/pro=10
        ₴1000-3000: none=10, c/b=15, a/pro=20
        ₴3000+: none=15, c/b=23, a/pro=30
        """
        rules = cls.objects.filter(
            rule_type='purchase',
            subscription_tier=user_subscription_tier,
            is_active=True
        ).order_by('min_amount')

        for rule in rules:
            if rule.min_amount is None:
                continue

            if amount < rule.min_amount:
                continue

            if rule.max_amount is None or amount <= rule.max_amount:
                return rule.points

        return 0

    @classmethod
    def get_points_for_subscription(cls, subscription_tier: str, duration_months: int) -> int:
        """
        Розрахувати бали за підписку:
        C/B-Vision: 1міс=15, 3міс=50, 6міс=100, 12міс=200
        A/Pro-Vision: 3міс=80, 6міс=160, 12міс=320
        """
        rule = cls.objects.filter(
            rule_type='subscription',
            subscription_tier=subscription_tier,
            subscription_duration_months=duration_months,
            is_active=True
        ).first()

        return rule.points if rule else 0


class RedemptionOption(models.Model):
    """
    Варіанти витрати балів
    """
    OPTION_TYPES = [
        ('discount', 'Знижка'),
        ('content_access', 'Доступ до контенту'),
        ('subscription_month', 'Місяць підписки'),
    ]

    SUBSCRIPTION_TIERS = [
        ('c_vision', 'C-Vision'),
        ('b_vision', 'B-Vision'),
    ]

    option_type = models.CharField(max_length=30, choices=OPTION_TYPES)
    name = models.CharField(max_length=100, help_text='Назва опції')
    description = models.TextField(blank=True)

    # Вартість в балах
    points_required = models.PositiveIntegerField(help_text='Скільки балів потрібно')

    # Для знижок
    discount_percentage = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Відсоток знижки (5, 10)'
    )

    # Для місяця підписки
    subscription_tier = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_TIERS,
        blank=True,
        help_text='Рівень підписки (тільки C/B-Vision)'
    )

    # Обмеження
    requires_subscription = models.BooleanField(
        default=False,
        help_text='Чи потрібна активна підписка для використання'
    )

    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'redemption_options'
        verbose_name = 'Redemption Option'
        verbose_name_plural = 'Redemption Options'
        ordering = ['display_order', 'points_required']

    def __str__(self):
        return f"{self.name} ({self.points_required} балів)"

    def can_redeem(self, user_points: int, has_subscription: bool = False) -> bool:
        """Перевірити чи користувач може використати цю опцію"""
        if not self.is_active:
            return False
        if user_points < self.points_required:
            return False
        if self.requires_subscription and not has_subscription:
            return False
        return True
