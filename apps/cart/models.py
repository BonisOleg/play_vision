from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal


class Cart(models.Model):
    """
    Shopping cart
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                           related_name='carts', null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True, help_text='For anonymous users')
    
    # Subscription suggestion tracking
    suggestion_shown = models.BooleanField(default=False, 
                                         help_text='Track if subscription suggestion was shown')
    suggestion_shown_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'carts'
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_key']),
        ]
    
    def __str__(self):
        if self.user:
            return f"Cart for {self.user.email}"
        return f"Cart for session {self.session_key}"
    
    def get_total(self):
        """Calculate cart total"""
        return sum(item.get_total() for item in self.items.all())
    
    def get_items_count(self):
        """Get total number of items"""
        return sum(item.quantity for item in self.items.all())
    
    def add_course(self, course, quantity=1):
        """Add course to cart"""
        item, created = self.items.get_or_create(
            item_type='course',
            item_id=course.id,
            defaults={
                'item_name': course.title,
                'price': course.price,
                'quantity': quantity
            }
        )
        if not created:
            item.quantity += quantity
            item.save()
        return item
    
    def add_subscription(self, plan):
        """Add subscription plan to cart"""
        # Remove other subscription plans first
        self.items.filter(item_type='subscription').delete()
        
        return self.items.create(
            item_type='subscription',
            item_id=plan.id,
            item_name=plan.name,
            price=plan.price,
            quantity=1
        )
    
    def clear(self):
        """Clear all items from cart"""
        self.items.all().delete()
    
    def merge_with(self, other_cart):
        """Merge another cart into this one"""
        for item in other_cart.items.all():
            existing = self.items.filter(
                item_type=item.item_type,
                item_id=item.item_id
            ).first()
            
            if existing:
                existing.quantity += item.quantity
                existing.save()
            else:
                item.cart = self
                item.save()
        
        other_cart.delete()


class CartItem(models.Model):
    """
    Items in shopping cart
    """
    ITEM_TYPE_CHOICES = [
        ('course', 'Course'),
        ('subscription', 'Subscription'),
        ('event_ticket', 'Event Ticket'),
    ]
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    item_id = models.PositiveIntegerField()
    item_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    # Metadata
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart_items'
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ['cart', 'item_type', 'item_id']
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.item_name} x{self.quantity}"
    
    def get_total(self):
        """Calculate item total"""
        return self.price * self.quantity
    
    def get_item_object(self):
        """Get the actual object this item represents"""
        if self.item_type == 'course':
            from apps.content.models import Course
            return Course.objects.filter(id=self.item_id).first()
        elif self.item_type == 'subscription':
            from apps.subscriptions.models import Plan
            return Plan.objects.filter(id=self.item_id).first()
        elif self.item_type == 'event_ticket':
            from apps.events.models import Event
            return Event.objects.filter(id=self.item_id).first()
        return None


class CartRecommendation(models.Model):
    """
    Product recommendations for cart
    """
    cart_item = models.ForeignKey(CartItem, on_delete=models.CASCADE, related_name='recommendations')
    recommended_type = models.CharField(max_length=20, choices=CartItem.ITEM_TYPE_CHOICES)
    recommended_id = models.PositiveIntegerField()
    recommended_name = models.CharField(max_length=200)
    reason = models.CharField(max_length=200, help_text='Why this is recommended')
    score = models.FloatField(default=0, help_text='Recommendation score')
    
    class Meta:
        db_table = 'cart_recommendations'
        verbose_name = 'Cart Recommendation'
        verbose_name_plural = 'Cart Recommendations'
        unique_together = ['cart_item', 'recommended_type', 'recommended_id']
        ordering = ['-score']
    
    def __str__(self):
        return f"Recommend {self.recommended_name} for {self.cart_item.item_name}"