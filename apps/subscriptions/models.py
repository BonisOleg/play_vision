"""
Моделі для системи підписок Play Vision
Створено: листопад 2025
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class SubscriptionPlan(models.Model):
    """
    Тарифний план підписки
    """
    
    # Кольори для бейджів
    BADGE_COLOR_CHOICES = [
        ('#3B82F6', 'Блакитний'),
        ('#F97316', 'Помаранчевий'),
        ('#E11D48', 'Червоний'),
        ('#EC4899', 'Рожевий'),
        ('#8B5CF6', 'Фіолетовий'),
        ('#10B981', 'Зелений'),
        ('#F59E0B', 'Жовтий'),
        ('#6B7280', 'Сірий'),
    ]
    
    # Основна інформація
    name = models.CharField(
        max_length=100,
        verbose_name='Назва тарифу',
        help_text='Наприклад: C-Vision, PRO-Vision'
    )
    
    slug = models.SlugField(
        unique=True,
        verbose_name='Slug (URL)',
        help_text='Автоматично генерується з назви'
    )
    
    # Бейдж
    badge_text = models.CharField(
        max_length=100,
        verbose_name='Текст бейджа',
        help_text='Наприклад: "Знайди свій PRO-Vision"',
        blank=True
    )
    
    badge_color = models.CharField(
        max_length=7,
        choices=BADGE_COLOR_CHOICES,
        default='#3B82F6',
        verbose_name='Колір бейджа'
    )
    
    # Переваги за періодами (monthly)
    feature_1_monthly = models.CharField(max_length=200, verbose_name='Перевага 1 (місяць)', blank=True)
    feature_2_monthly = models.CharField(max_length=200, verbose_name='Перевага 2 (місяць)', blank=True)
    feature_3_monthly = models.CharField(max_length=200, verbose_name='Перевага 3 (місяць)', blank=True)
    feature_4_monthly = models.CharField(max_length=200, verbose_name='Перевага 4 (місяць)', blank=True)
    feature_5_monthly = models.CharField(max_length=200, verbose_name='Перевага 5 (місяць)', blank=True)
    feature_6_monthly = models.CharField(max_length=200, verbose_name='Перевага 6 (місяць)', blank=True)
    feature_7_monthly = models.CharField(max_length=200, verbose_name='Перевага 7 (місяць)', blank=True)
    feature_8_monthly = models.CharField(max_length=200, verbose_name='Перевага 8 (місяць)', blank=True)
    feature_9_monthly = models.CharField(max_length=200, verbose_name='Перевага 9 (місяць)', blank=True)
    feature_10_monthly = models.CharField(max_length=200, verbose_name='Перевага 10 (місяць)', blank=True)
    feature_11_monthly = models.CharField(max_length=200, verbose_name='Перевага 11 (місяць)', blank=True)
    feature_12_monthly = models.CharField(max_length=200, verbose_name='Перевага 12 (місяць)', blank=True)
    feature_13_monthly = models.CharField(max_length=200, verbose_name='Перевага 13 (місяць)', blank=True)
    feature_14_monthly = models.CharField(max_length=200, verbose_name='Перевага 14 (місяць)', blank=True)
    feature_15_monthly = models.CharField(max_length=200, verbose_name='Перевага 15 (місяць)', blank=True)
    feature_16_monthly = models.CharField(max_length=200, verbose_name='Перевага 16 (місяць)', blank=True)
    feature_17_monthly = models.CharField(max_length=200, verbose_name='Перевага 17 (місяць)', blank=True)
    feature_18_monthly = models.CharField(max_length=200, verbose_name='Перевага 18 (місяць)', blank=True)
    feature_19_monthly = models.CharField(max_length=200, verbose_name='Перевага 19 (місяць)', blank=True)
    feature_20_monthly = models.CharField(max_length=200, verbose_name='Перевага 20 (місяць)', blank=True)
    feature_21_monthly = models.CharField(max_length=200, verbose_name='Перевага 21 (місяць)', blank=True)
    feature_22_monthly = models.CharField(max_length=200, verbose_name='Перевага 22 (місяць)', blank=True)
    feature_23_monthly = models.CharField(max_length=200, verbose_name='Перевага 23 (місяць)', blank=True)
    feature_24_monthly = models.CharField(max_length=200, verbose_name='Перевага 24 (місяць)', blank=True)
    feature_25_monthly = models.CharField(max_length=200, verbose_name='Перевага 25 (місяць)', blank=True)
    feature_26_monthly = models.CharField(max_length=200, verbose_name='Перевага 26 (місяць)', blank=True)
    feature_27_monthly = models.CharField(max_length=200, verbose_name='Перевага 27 (місяць)', blank=True)
    feature_28_monthly = models.CharField(max_length=200, verbose_name='Перевага 28 (місяць)', blank=True)
    feature_29_monthly = models.CharField(max_length=200, verbose_name='Перевага 29 (місяць)', blank=True)
    feature_30_monthly = models.CharField(max_length=200, verbose_name='Перевага 30 (місяць)', blank=True)
    
    # Переваги за періодами (3_months)
    feature_1_3months = models.CharField(max_length=200, verbose_name='Перевага 1 (3 міс)', blank=True)
    feature_2_3months = models.CharField(max_length=200, verbose_name='Перевага 2 (3 міс)', blank=True)
    feature_3_3months = models.CharField(max_length=200, verbose_name='Перевага 3 (3 міс)', blank=True)
    feature_4_3months = models.CharField(max_length=200, verbose_name='Перевага 4 (3 міс)', blank=True)
    feature_5_3months = models.CharField(max_length=200, verbose_name='Перевага 5 (3 міс)', blank=True)
    feature_6_3months = models.CharField(max_length=200, verbose_name='Перевага 6 (3 міс)', blank=True)
    feature_7_3months = models.CharField(max_length=200, verbose_name='Перевага 7 (3 міс)', blank=True)
    feature_8_3months = models.CharField(max_length=200, verbose_name='Перевага 8 (3 міс)', blank=True)
    feature_9_3months = models.CharField(max_length=200, verbose_name='Перевага 9 (3 міс)', blank=True)
    feature_10_3months = models.CharField(max_length=200, verbose_name='Перевага 10 (3 міс)', blank=True)
    feature_11_3months = models.CharField(max_length=200, verbose_name='Перевага 11 (3 міс)', blank=True)
    feature_12_3months = models.CharField(max_length=200, verbose_name='Перевага 12 (3 міс)', blank=True)
    feature_13_3months = models.CharField(max_length=200, verbose_name='Перевага 13 (3 міс)', blank=True)
    feature_14_3months = models.CharField(max_length=200, verbose_name='Перевага 14 (3 міс)', blank=True)
    feature_15_3months = models.CharField(max_length=200, verbose_name='Перевага 15 (3 міс)', blank=True)
    feature_16_3months = models.CharField(max_length=200, verbose_name='Перевага 16 (3 міс)', blank=True)
    feature_17_3months = models.CharField(max_length=200, verbose_name='Перевага 17 (3 міс)', blank=True)
    feature_18_3months = models.CharField(max_length=200, verbose_name='Перевага 18 (3 міс)', blank=True)
    feature_19_3months = models.CharField(max_length=200, verbose_name='Перевага 19 (3 міс)', blank=True)
    feature_20_3months = models.CharField(max_length=200, verbose_name='Перевага 20 (3 міс)', blank=True)
    feature_21_3months = models.CharField(max_length=200, verbose_name='Перевага 21 (3 міс)', blank=True)
    feature_22_3months = models.CharField(max_length=200, verbose_name='Перевага 22 (3 міс)', blank=True)
    feature_23_3months = models.CharField(max_length=200, verbose_name='Перевага 23 (3 міс)', blank=True)
    feature_24_3months = models.CharField(max_length=200, verbose_name='Перевага 24 (3 міс)', blank=True)
    feature_25_3months = models.CharField(max_length=200, verbose_name='Перевага 25 (3 міс)', blank=True)
    feature_26_3months = models.CharField(max_length=200, verbose_name='Перевага 26 (3 міс)', blank=True)
    feature_27_3months = models.CharField(max_length=200, verbose_name='Перевага 27 (3 міс)', blank=True)
    feature_28_3months = models.CharField(max_length=200, verbose_name='Перевага 28 (3 міс)', blank=True)
    feature_29_3months = models.CharField(max_length=200, verbose_name='Перевага 29 (3 міс)', blank=True)
    feature_30_3months = models.CharField(max_length=200, verbose_name='Перевага 30 (3 міс)', blank=True)
    
    # Ціноутворення - нова логіка
    # Місячна підписка
    original_price_monthly_uah = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Ціна до знижки (грн/міс)',
        help_text='Ціна за місяць до знижки в гривнях',
        default=0
    )
    
    original_price_monthly_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Ціна до знижки ($/міс)',
        help_text='Ціна за місяць до знижки в доларах',
        default=0
    )
    
    sale_price_monthly_uah = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Ціна після знижки (грн/міс)',
        help_text='Ціна за місяць після знижки в гривнях',
        default=0
    )
    
    sale_price_monthly_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Ціна після знижки ($/міс)',
        help_text='Ціна за місяць після знижки в доларах',
        default=0
    )
    
    # 3-місячна підписка
    original_price_3months_uah = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Ціна до знижки за 3 місяці (грн)',
        help_text='Ціна за 3 місяці до знижки в гривнях',
        default=0
    )
    
    original_price_3months_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Ціна до знижки за 3 місяці ($)',
        help_text='Ціна за 3 місяці до знижки в доларах',
        default=0
    )
    
    sale_price_3months_uah = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Ціна після знижки за 3 місяці (грн)',
        help_text='Ціна за 3 місяці після знижки в гривнях',
        default=0
    )
    
    sale_price_3months_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Ціна після знижки за 3 місяці ($)',
        help_text='Ціна за 3 місяці після знижки в доларах',
        default=0
    )
    
    # Таймери знижок (контролюють, коли показувати знижку)
    discount_monthly_start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Початок знижки (місяць)',
        help_text='Дата початку дії знижки. Якщо встановлено, sale_price буде показано в період між start_date та end_date'
    )
    discount_monthly_end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Кінець знижки (місяць)',
        help_text='Дата закінчення дії знижки'
    )
    discount_3months_start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Початок знижки (3 міс)',
        help_text='Дата початку дії знижки. Якщо встановлено, sale_price буде показано в період між start_date та end_date'
    )
    discount_3months_end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Кінець знижки (3 міс)',
        help_text='Дата закінчення дії знижки'
    )
    
    # Старі поля (будуть видалені в міграції, але залишаються для конвертації)
    base_price_uah = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='[DEPRECATED] Базова ціна (грн/міс)',
        help_text='DEPRECATED: Використовуйте original_price_monthly_uah',
        default=0,
        null=True,
        blank=True
    )
    
    base_price_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='[DEPRECATED] Базова ціна ($/міс)',
        help_text='DEPRECATED: Використовуйте original_price_monthly_usd',
        default=0,
        null=True,
        blank=True
    )
    
    base_price_3months_uah = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='[DEPRECATED] Базова ціна за 3 місяці (грн)',
        help_text='DEPRECATED: Використовуйте original_price_3months_uah',
        default=0,
        null=True,
        blank=True
    )
    
    base_price_3months_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='[DEPRECATED] Базова ціна за 3 місяці ($)',
        help_text='DEPRECATED: Використовуйте original_price_3months_usd',
        default=0,
        null=True,
        blank=True
    )
    
    discount_3_months = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='[DEPRECATED] Знижка на 3 місяці (%)',
        help_text='DEPRECATED: Відсоток розраховується автоматично',
        null=True,
        blank=True
    )
    
    discount_monthly = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='[DEPRECATED] Знижка на місяць (%)',
        help_text='DEPRECATED: Відсоток розраховується автоматично',
        null=True,
        blank=True
    )
    
    discount_monthly_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='[DEPRECATED] Знижка на місяць (%)',
        help_text='DEPRECATED: Відсоток розраховується автоматично',
        null=True,
        blank=True
    )
    
    discount_3months_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='[DEPRECATED] Знижка на 3 місяці (%)',
        help_text='DEPRECATED: Відсоток розраховується автоматично',
        null=True,
        blank=True
    )
    
    # Доступність періодів
    available_monthly = models.BooleanField(
        default=True,
        verbose_name='Доступно на місяць'
    )
    
    available_3_months = models.BooleanField(
        default=True,
        verbose_name='Доступно на 3 місяці'
    )
    
    unavailable_text = models.CharField(
        max_length=100,
        default='Доступно в тарифі від 3 місяців',
        verbose_name='Текст для недоступних періодів',
        help_text='Показується замість кнопки, коли період недоступний'
    )
    
    # Зовнішнє посилання
    checkout_url = models.URLField(
        verbose_name='URL сторінки оплати',
        help_text='Посилання на зовнішній сервіс квітка',
        blank=True
    )
    
    # Відображення
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок відображення',
        help_text='Чим менше число, тим раніше відображається'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активний',
        help_text='Показувати на сайті'
    )
    
    is_popular = models.BooleanField(
        default=False,
        verbose_name='Популярний',
        help_text='Виділити як найпопулярніший тариф'
    )
    
    # SEO
    meta_title = models.CharField(
        max_length=200,
        verbose_name='Meta Title',
        blank=True,
        help_text='Для SEO (залиште порожнім для автогенерації)'
    )
    
    meta_description = models.TextField(
        max_length=300,
        verbose_name='Meta Description',
        blank=True,
        help_text='Для SEO'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Створено')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Оновлено')
    
    class Meta:
        db_table = 'subscription_plans'
        verbose_name = 'Тарифний план'
        verbose_name_plural = 'Тарифні плани'
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_features(self, period='monthly'):
        """
        Повертає список заповнених переваг для конкретного періоду
        
        Args:
            period: 'monthly' або '3_months'
        
        Returns:
            list: Список заповнених переваг
        """
        features = []
        period_suffix = 'monthly' if period == 'monthly' else '3months'
        
        for i in range(1, 31):
            feature = getattr(self, f'feature_{i}_{period_suffix}', '')
            if feature:
                features.append(feature)
        
        return features
    
    def is_discount_active(self, period):
        """
        Перевіряє чи активний таймер знижки для періоду
        
        Args:
            period: 'monthly' або '3_months'
        
        Returns:
            bool: True якщо таймер активний
        """
        now = timezone.now()
        
        if period == 'monthly':
            return (self.discount_monthly_start_date and 
                   self.discount_monthly_end_date and
                   self.discount_monthly_start_date <= now <= self.discount_monthly_end_date)
        elif period == '3_months':
            return (self.discount_3months_start_date and 
                   self.discount_3months_end_date and
                   self.discount_3months_start_date <= now <= self.discount_3months_end_date)
        
        return False
    
    def get_original_price(self, period, currency='uah'):
        """
        Повертає ціну до знижки для періоду
        
        Args:
            period: 'monthly' або '3_months'
            currency: 'uah' або 'usd'
        
        Returns:
            Decimal: Ціна до знижки
        """
        from decimal import Decimal
        
        if period == 'monthly':
            return Decimal(str(self.original_price_monthly_uah if currency == 'uah' else self.original_price_monthly_usd))
        elif period == '3_months':
            return Decimal(str(self.original_price_3months_uah if currency == 'uah' else self.original_price_3months_usd))
        
        return Decimal('0')
    
    def get_sale_price(self, period, currency='uah'):
        """
        Повертає ціну після знижки для періоду
        
        Args:
            period: 'monthly' або '3_months'
            currency: 'uah' або 'usd'
        
        Returns:
            Decimal: Ціна після знижки
        """
        from decimal import Decimal
        
        if period == 'monthly':
            return Decimal(str(self.sale_price_monthly_uah if currency == 'uah' else self.sale_price_monthly_usd))
        elif period == '3_months':
            return Decimal(str(self.sale_price_3months_uah if currency == 'uah' else self.sale_price_3months_usd))
        
        return Decimal('0')
    
    def get_discount_percentage(self, period, currency='uah'):
        """
        Розраховує відсоток знижки автоматично на основі original_price та sale_price
        
        Args:
            period: 'monthly' або '3_months'
            currency: 'uah' або 'usd'
        
        Returns:
            int: Відсоток знижки (0-100) або 0
        """
        from decimal import Decimal
        
        original = self.get_original_price(period, currency)
        sale = self.get_sale_price(period, currency)
        
        if original == 0:
            return 0
        
        if sale >= original:
            return 0  # Немає знижки
        
        discount = ((original - sale) / original) * Decimal('100')
        return int(discount)
    
    def get_active_discount(self, period):
        """
        Повертає активну знижку для періоду (відсоток)
        Якщо таймер активний, повертає відсоток знижки, інакше 0
        
        Args:
            period: 'monthly' або '3_months'
        
        Returns:
            int: Відсоток знижки або 0
        """
        if self.is_discount_active(period):
            # Визначаємо валюту за замовчуванням (можна розширити)
            return self.get_discount_percentage(period, 'uah')
        
        return 0
    
    def get_discount_time_left(self, period):
        """
        Повертає час до закінчення знижки
        
        Args:
            period: 'monthly' або '3_months'
        
        Returns:
            timedelta або None
        """
        now = timezone.now()
        
        if period == 'monthly':
            if self.discount_monthly_end_date and self.discount_monthly_end_date > now:
                return self.discount_monthly_end_date - now
        elif period == '3_months':
            if self.discount_3months_end_date and self.discount_3months_end_date > now:
                return self.discount_3months_end_date - now
        
        return None
    
    def calculate_price(self, period, currency='uah'):
        """
        Розраховує ціну з урахуванням періоду та таймера знижки
        Якщо таймер активний - повертає sale_price, інакше original_price
        
        Args:
            period: 'monthly', '3_months'
            currency: 'uah' або 'usd'
        
        Returns:
            Decimal: Фінальна ціна
        """
        original = self.get_original_price(period, currency)
        sale = self.get_sale_price(period, currency)
        
        # Якщо таймер активний, показуємо ціну зі знижкою
        if self.is_discount_active(period):
            # Якщо sale_price не встановлено, повертаємо original
            if sale > 0:
                return sale
        
        # Якщо таймер не активний або sale_price не встановлено, повертаємо original
        return original if original > 0 else sale
    
    def get_monthly_price(self, period, currency='uah'):
        """Розраховує ціну за місяць для кожного періоду"""
        from decimal import Decimal
        
        total_price = self.calculate_price(period, currency)
        
        if period == 'monthly':
            return total_price
        elif period == '3_months':
            return total_price / Decimal('3')
        
        return total_price
    
    def is_period_available(self, period):
        """Перевіряє чи доступний період"""
        if period == 'monthly':
            return self.available_monthly
        elif period == '3_months':
            return self.available_3_months
        return False
    
    def get_checkout_url(self, period='monthly'):
        """
        Повертає посилання на оплату залежно від плану та періоду
        
        Args:
            period: 'monthly' або '3_months'
        
        Returns:
            str: URL для оплати
        """
        plan_name_lower = self.name.lower()
        
        # C-Vision посилання
        if 'c-vision' in plan_name_lower or 'c_vision' in plan_name_lower:
            if period == 'monthly':
                return 'https://edu.playvision.com.ua/o/W2INE2aFFjt7/payment/2756'
            elif period == '3_months':
                return 'https://edu.playvision.com.ua/o/ldxmHjV6K85M/payment/2756'
        
        # B-Vision посилання
        elif 'b-vision' in plan_name_lower or 'b_vision' in plan_name_lower:
            if period == 'monthly':
                return 'https://edu.playvision.com.ua/o/kCHKbeCtLCSs/payment/2756'
            elif period == '3_months':
                return 'https://edu.playvision.com.ua/o/cg8MMFAGeVED/payment/2756'
        
        # Fallback на checkout_url для інших планів
        if self.checkout_url:
            return self.checkout_url
        
        return ''
    
    def save(self, *args, **kwargs):
        """Автогенерація slug з назви"""
        if not self.slug:
            from django.utils.text import slugify
            from transliterate import translit
            # Транслітерація кирилиці
            try:
                transliterated = translit(self.name, 'uk', reversed=True)
                self.slug = slugify(transliterated)
            except:
                self.slug = slugify(self.name)
        
        super().save(*args, **kwargs)


# Backward compatibility aliases
Plan = SubscriptionPlan


class Subscription(models.Model):
    """
    User subscription instance (temporarily minimal for compatibility)
    TODO: Expand this model or integrate with external subscription service
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscriptions'
        verbose_name = 'Підписка користувача'
        verbose_name_plural = 'Підписки користувачів'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"
    
    @property
    def is_expired(self):
        """Check if subscription is expired"""
        return timezone.now() > self.end_date

