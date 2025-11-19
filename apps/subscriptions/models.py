"""
Моделі для системи підписок Play Vision
Створено: листопад 2025
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


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
    
    # Переваги (від 1 до 5)
    feature_1 = models.CharField(
        max_length=200,
        verbose_name='Перевага 1',
        help_text='Обов\'язкова'
    )
    
    feature_2 = models.CharField(
        max_length=200,
        verbose_name='Перевага 2',
        blank=True
    )
    
    feature_3 = models.CharField(
        max_length=200,
        verbose_name='Перевага 3',
        blank=True
    )
    
    feature_4 = models.CharField(
        max_length=200,
        verbose_name='Перевага 4',
        blank=True
    )
    
    feature_5 = models.CharField(
        max_length=200,
        verbose_name='Перевага 5',
        blank=True
    )
    
    # Ціноутворення
    base_price_uah = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Базова ціна (грн/міс)',
        help_text='Ціна за 1 місяць в гривнях'
    )
    
    base_price_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Базова ціна ($/міс)',
        help_text='Ціна за 1 місяць в доларах'
    )
    
    discount_3_months = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Знижка на 3 місяці (%)',
        help_text='Відсоток знижки для 3-місячної підписки'
    )
    
    discount_12_months = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Знижка на рік (%)',
        help_text='Відсоток знижки для річної підписки'
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
    
    available_12_months = models.BooleanField(
        default=True,
        verbose_name='Доступно на рік'
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
    
    def get_features(self):
        """Повертає список заповнених переваг"""
        features = []
        for i in range(1, 6):
            feature = getattr(self, f'feature_{i}', '')
            if feature:
                features.append(feature)
        return features
    
    def calculate_price(self, period, currency='uah'):
        """
        Розраховує ціну з урахуванням періоду та знижки
        
        Args:
            period: 'monthly', '3_months', '12_months'
            currency: 'uah' або 'usd'
        
        Returns:
            Decimal: Фінальна ціна
        """
        base_price = self.base_price_uah if currency == 'uah' else self.base_price_usd
        
        if period == 'monthly':
            return base_price
        
        elif period == '3_months':
            full_price = base_price * 3
            discount = self.discount_3_months
            return full_price * (1 - discount / 100)
        
        elif period == '12_months':
            full_price = base_price * 12
            discount = self.discount_12_months
            return full_price * (1 - discount / 100)
        
        return base_price
    
    def get_monthly_price(self, period, currency='uah'):
        """Розраховує ціну за місяць для кожного періоду"""
        total_price = self.calculate_price(period, currency)
        
        if period == 'monthly':
            return total_price
        elif period == '3_months':
            return total_price / 3
        elif period == '12_months':
            return total_price / 12
        
        return total_price
    
    def is_period_available(self, period):
        """Перевіряє чи доступний період"""
        if period == 'monthly':
            return self.available_monthly
        elif period == '3_months':
            return self.available_3_months
        elif period == '12_months':
            return self.available_12_months
        return False
    
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

