from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal


class LoyaltyTier(models.Model):
    """
    Loyalty program tiers: Bronze, Silver, Gold, Platinum
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
        verbose_name = 'Loyalty Tier'
        verbose_name_plural = 'Loyalty Tiers'
    
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
    User loyalty account with points and tier tracking
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                               related_name='loyalty_account')
    points = models.PositiveIntegerField(default=0)
    lifetime_points = models.PositiveIntegerField(default=0, help_text='Total points earned ever')
    lifetime_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0, 
                                       help_text='Total money spent')
    current_tier = models.ForeignKey(LoyaltyTier, on_delete=models.PROTECT, 
                                   related_name='users', null=True, blank=True)
    tier_achieved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'loyalty_accounts'
        verbose_name = 'Loyalty Account'
        verbose_name_plural = 'Loyalty Accounts'
    
    def __str__(self):
        tier_name = self.current_tier.name if self.current_tier else 'No Tier'
        return f"{self.user.email} - {tier_name} ({self.points} points)"
    
    def get_discount_percentage(self):
        """Get current discount percentage"""
        if self.current_tier:
            return self.current_tier.discount_percentage
        return 0
    
    def update_tier(self):
        """Update tier based on current points"""
        new_tier = LoyaltyTier.get_tier_for_points(self.points)
        if new_tier and new_tier != self.current_tier:
            old_tier = self.current_tier
            self.current_tier = new_tier
            self.tier_achieved_at = timezone.now()
            self.save()
            
            # Створити транзакцію для нарахування бонусних балів за досягнення рівня
            if old_tier and new_tier.points_required > old_tier.points_required:
                bonus_points = 10  # Бонус за підвищення рівня
                self.add_points(
                    bonus_points, 
                    'tier_achievement', 
                    f'Бонус за досягнення рівня {new_tier.name}'
                )
            
            return True
        return False
    
    def add_points(self, points, transaction_type='earned', reason=''):
        """Add points and create transaction"""
        self.points += points
        self.lifetime_points += points
        self.save()
        
        # Створити транзакцію
        PointTransaction.objects.create(
            account=self,
            points=points,
            transaction_type=transaction_type,
            reason=reason,
            balance_after=self.points
        )
        
        # Перевірити зміну рівня (without recursion)
        new_tier = LoyaltyTier.get_tier_for_points(self.points)
        if new_tier and new_tier != self.current_tier:
            self.current_tier = new_tier
            self.tier_achieved_at = timezone.now()
            self.save()
        
        return self.points
    
    def get_next_tier(self):
        """Get next tier to achieve"""
        if not self.current_tier:
            return LoyaltyTier.objects.filter(is_active=True).order_by('points_required').first()
        
        return LoyaltyTier.objects.filter(
            points_required__gt=self.current_tier.points_required,
            is_active=True
        ).order_by('points_required').first()
    
    def points_to_next_tier(self):
        """Calculate points needed for next tier"""
        next_tier = self.get_next_tier()
        if next_tier:
            return max(0, next_tier.points_required - self.points)
        return 0
    
    def progress_to_next_tier(self):
        """Calculate progress percentage to next tier"""
        next_tier = self.get_next_tier()
        if not next_tier:
            return 100  # Max tier reached
        
        current_tier_points = self.current_tier.points_required if self.current_tier else 0
        points_range = next_tier.points_required - current_tier_points
        current_progress = self.points - current_tier_points
        
        if points_range <= 0:
            return 100
        
        return min(100, max(0, (current_progress / points_range) * 100))


class PointTransaction(models.Model):
    """
    Points earning/spending transaction history
    """
    TRANSACTION_TYPES = [
        ('earned', 'Earned'),
        ('spent', 'Spent'),
        ('expired', 'Expired'),
        ('adjusted', 'Adjusted'),
    ]
    
    account = models.ForeignKey(LoyaltyAccount, on_delete=models.CASCADE, 
                              related_name='point_transactions')
    points = models.IntegerField(help_text='Positive for earned, negative for spent')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    reason = models.CharField(max_length=200, help_text='Why points were added/removed')
    reference_type = models.CharField(max_length=50, blank=True)
    reference_id = models.PositiveIntegerField(null=True, blank=True)
    balance_after = models.PositiveIntegerField(help_text='Points balance after this transaction')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'point_transactions'
        verbose_name = 'Point Transaction'
        verbose_name_plural = 'Point Transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        action = "earned" if self.points > 0 else "spent"
        return f"{self.account.user.email} {action} {abs(self.points)} points"