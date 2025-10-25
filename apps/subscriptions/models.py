from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator


class Plan(models.Model):
    """
    Subscription plans
    """
    DURATION_CHOICES = [
        ('1_month', '1 місяць'),
        ('3_months', '3 місяці'), 
        ('12_months', '12 місяців'),
    ]
    
    BADGE_CHOICES = [
        ('popular', 'Найпопулярніший'),
        ('best_value', 'Максимальна економія'),
        ('recommended', 'Рекомендуємо'),
        ('new', 'Новинка'),
    ]
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES)
    duration_months = models.PositiveIntegerField(help_text='Duration in months')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Features
    features = models.JSONField(default=list, help_text='List of plan features')
    event_tickets_balance = models.IntegerField(default=0, help_text='Monthly event tickets for Pro-Vision')
    discount_percentage = models.IntegerField(default=0, help_text='Loyalty discount percentage')
    
    # Display
    is_popular = models.BooleanField(default=False, help_text='Mark as popular plan')
    is_best_value = models.BooleanField(default=False, help_text='Mark as best value (auto-set for longest duration)')
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    badge_text = models.CharField(max_length=50, blank=True, help_text='Custom badge text (optional)')
    badge_type = models.CharField(max_length=20, choices=BADGE_CHOICES, blank=True)
    
    # Statistics for auto-badge detection
    total_subscriptions = models.PositiveIntegerField(default=0, help_text='Total number of subscriptions sold')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscription_plans'
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'
        ordering = ['display_order', 'duration_months']
    
    def __str__(self):
        return f"{self.name} ({self.get_duration_display()})"
    
    @property
    def monthly_price(self):
        """Calculate monthly price"""
        return self.price / self.duration_months if self.duration_months else 0
    
    @property
    def savings_percentage(self):
        """Calculate savings compared to monthly plan"""
        if self.duration_months <= 1:
            return 0
        monthly_plan = Plan.objects.filter(duration='1_month', is_active=True).first()
        if monthly_plan:
            full_price = monthly_plan.price * self.duration_months
            savings = ((full_price - self.price) / full_price) * 100
            return int(savings)
        return 0
    
    @property
    def auto_badge(self):
        """
        Автоматичне визначення бейджа
        Пріоритет: is_popular > is_best_value > highest savings
        """
        if self.badge_text:
            return self.badge_text
        
        if self.is_popular:
            return 'Найпопулярніший'
        
        if self.is_best_value or self.savings_percentage >= 30:
            return 'Максимальна економія'
        
        if self.savings_percentage >= 15:
            return 'Вигідно'
        
        return ''
    
    @property
    def badge_class(self):
        """CSS клас для бейджа"""
        if self.is_popular:
            return 'badge-popular'
        if self.is_best_value or self.savings_percentage >= 30:
            return 'badge-best-value'
        if self.savings_percentage >= 15:
            return 'badge-good-value'
        return 'badge-default'
    
    def save(self, *args, **kwargs):
        """Автоматично визначаємо найвигідніший план"""
        # Якщо це найдовший термін - позначаємо як best_value
        if self.is_active:
            all_plans = Plan.objects.filter(is_active=True)
            if all_plans.exists():
                max_duration = all_plans.aggregate(max_months=models.Max('duration_months'))['max_months']
                if self.duration_months == max_duration:
                    # Знімаємо best_value з інших планів
                    Plan.objects.filter(is_best_value=True).exclude(id=self.id).update(is_best_value=False)
                    self.is_best_value = True
        
        super().save(*args, **kwargs)
    
    @classmethod
    def get_most_popular(cls):
        """Отримати найпопулярніший план (за кількістю підписок)"""
        return cls.objects.filter(is_active=True).order_by('-total_subscriptions').first()
    
    @classmethod
    def get_best_value(cls):
        """Отримати план з найбільшою економією"""
        plans = cls.objects.filter(is_active=True)
        best_plan = None
        max_savings = 0
        
        for plan in plans:
            if plan.savings_percentage > max_savings:
                max_savings = plan.savings_percentage
                best_plan = plan
        
        return best_plan


class Subscription(models.Model):
    """
    User subscriptions
    """
    STATUS_CHOICES = [
        ('trial', 'Trial'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('past_due', 'Past Due'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Dates
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    trial_end_date = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Billing
    auto_renew = models.BooleanField(default=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscriptions'
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['end_date']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name} ({self.status})"
    
    @property
    def is_active(self):
        """Check if subscription is currently active"""
        return (
            self.status == 'active' and
            self.start_date <= timezone.now() <= self.end_date
        )
    
    @property
    def days_remaining(self):
        """Days until subscription ends"""
        if self.is_active:
            delta = self.end_date - timezone.now()
            return delta.days
        return 0
    
    def cancel(self):
        """Cancel subscription"""
        self.status = 'cancelled'
        self.auto_renew = False
        self.cancelled_at = timezone.now()
        self.save()
    
    def pause(self):
        """Pause subscription"""
        if self.status == 'active':
            self.status = 'paused'
            self.save()
    
    def resume(self):
        """Resume paused subscription"""
        if self.status == 'paused':
            self.status = 'active'
            self.save()


class Entitlement(models.Model):
    """
    Content access entitlements granted by subscriptions
    """
    CONTENT_TYPES = [
        ('course', 'Course'),
        ('event', 'Event'),
        ('feature', 'Feature'),
    ]
    
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='entitlements')
    content_type = models.CharField(max_length=50, choices=CONTENT_TYPES)
    content_id = models.IntegerField(null=True, blank=True, help_text='ID of specific content, null for all')
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'entitlements'
        verbose_name = 'Entitlement'
        verbose_name_plural = 'Entitlements'
        indexes = [
            models.Index(fields=['subscription', 'content_type']),
        ]
    
    def __str__(self):
        return f"{self.subscription} - {self.content_type}"
    
    @property
    def is_valid(self):
        """Check if entitlement is still valid"""
        if self.expires_at:
            return timezone.now() < self.expires_at
        return self.subscription.is_active


class TicketBalance(models.Model):
    """
    Event ticket balance for Pro-Vision subscribers
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ticket_balances')
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='ticket_balances')
    amount = models.PositiveIntegerField(default=0)
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'ticket_balances'
        verbose_name = 'Ticket Balance'
        verbose_name_plural = 'Ticket Balances'
        ordering = ['expires_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.amount} tickets"
    
    @property
    def is_valid(self):
        """Check if balance is still valid"""
        return self.amount > 0 and timezone.now() < self.expires_at