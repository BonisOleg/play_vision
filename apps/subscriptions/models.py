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
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    badge_text = models.CharField(max_length=50, blank=True, help_text='e.g. "Найпопулярніший"')
    
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