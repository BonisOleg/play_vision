from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Payment(models.Model):
    """
    Payment transactions
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('requires_action', 'Requires Action'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('partial_refund', 'Partial Refund'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('subscription', 'Subscription'),
        ('course', 'Course'),
        ('event_ticket', 'Event Ticket'),
        ('bundle', 'Bundle'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default='UAH')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    
    # Payment provider data
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True, unique=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True)
    provider_response = models.JSONField(default=dict, blank=True)
    
    # 3DS data
    requires_3ds = models.BooleanField(default=False)
    client_secret = models.CharField(max_length=200, blank=True)
    
    # Metadata
    description = models.CharField(max_length=500, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['stripe_payment_intent_id']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.amount} {self.currency} ({self.status})"
    
    def mark_succeeded(self):
        """Mark payment as succeeded"""
        self.status = 'succeeded'
        self.completed_at = timezone.now()
        self.save()
    
    def mark_failed(self):
        """Mark payment as failed"""
        self.status = 'failed'
        self.save()


class Order(models.Model):
    """
    Order containing multiple items
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Payment'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Coupon
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Payment
    payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='order')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number} - {self.user.email}"
    
    def calculate_totals(self):
        """Recalculate order totals"""
        self.subtotal = sum(item.total for item in self.items.all())
        
        # Apply coupon discount
        if self.coupon:
            if self.coupon.discount_type == 'percentage':
                self.discount_amount = self.subtotal * (self.coupon.discount_value / 100)
            else:
                self.discount_amount = min(self.coupon.discount_value, self.subtotal)
        
        self.total = self.subtotal - self.discount_amount + self.tax_amount
        self.save()
    
    def mark_completed(self):
        """Mark order as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()


class OrderItem(models.Model):
    """
    Individual items in an order
    """
    ITEM_TYPE_CHOICES = [
        ('course', 'Course'),
        ('subscription', 'Subscription'),
        ('event_ticket', 'Event Ticket'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    item_id = models.PositiveIntegerField()
    item_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'order_items'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
    
    def __str__(self):
        return f"{self.item_name} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        self.total = self.price * self.quantity
        super().save(*args, **kwargs)


class Coupon(models.Model):
    """
    Discount coupons
    """
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200, blank=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Restrictions
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, 
                                   help_text='Minimum order amount required')
    max_uses = models.PositiveIntegerField(null=True, blank=True, 
                                         help_text='Leave empty for unlimited')
    used_count = models.PositiveIntegerField(default=0)
    once_per_user = models.BooleanField(default=False)
    
    # Validity
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'coupons'
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
        indexes = [
            models.Index(fields=['code', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.get_discount_display()}"
    
    def get_discount_display(self):
        """Get human-readable discount"""
        if self.discount_type == 'percentage':
            return f"{int(self.discount_value)}%"
        return f"{self.discount_value} UAH"
    
    @property
    def is_valid(self):
        """Check if coupon is currently valid"""
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_until and
            (self.max_uses is None or self.used_count < self.max_uses)
        )
    
    def can_be_used_by(self, user):
        """Check if user can use this coupon"""
        if not self.is_valid:
            return False
        
        if self.once_per_user and user.is_authenticated:
            return not CouponUsage.objects.filter(
                coupon=self,
                user=user
            ).exists()
        
        return True


class CouponUsage(models.Model):
    """
    Track coupon usage by users
    """
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='coupon_usages')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='coupon_usages')
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'coupon_usages'
        verbose_name = 'Coupon Usage'
        verbose_name_plural = 'Coupon Usages'
        unique_together = ['coupon', 'order']
    
    def __str__(self):
        return f"{self.user.email} used {self.coupon.code}"


class WebhookEvent(models.Model):
    """
    Store webhook events for idempotency
    """
    event_id = models.CharField(max_length=200, unique=True)
    event_type = models.CharField(max_length=50)
    payload = models.JSONField()
    processed = models.BooleanField(default=False)
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'webhook_events'
        verbose_name = 'Webhook Event'
        verbose_name_plural = 'Webhook Events'
        indexes = [
            models.Index(fields=['event_id']),
            models.Index(fields=['event_type', 'processed']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.event_id}"