from django.views.generic import TemplateView
from django.utils import timezone
from .models import LoyaltyTier, LoyaltyAccount, PointEarningRule, RedemptionOption


class LoyaltyRulesView(TemplateView):
    """
    Сторінка з правилами програми лояльності
    """
    template_name = 'loyalty/rules.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Інформація про користувача (якщо залогінений)
        if self.request.user.is_authenticated:
            try:
                loyalty_account = self.request.user.loyalty_account
                context['user_points'] = loyalty_account.points
                context['user_lifetime_points'] = loyalty_account.lifetime_points
                
                # Активна підписка
                active_subscription = self.request.user.subscriptions.filter(
                    status='active',
                    end_date__gte=timezone.now()
                ).first()
                context['active_subscription'] = active_subscription
                
            except LoyaltyAccount.DoesNotExist:
                context['user_points'] = 0
                context['user_lifetime_points'] = 0
                context['active_subscription'] = None
        else:
            context['user_points'] = 0
            context['user_lifetime_points'] = 0
            context['active_subscription'] = None
        
        # Правила нарахування балів (за покупки)
        purchase_rules = PointEarningRule.objects.filter(
            rule_type='purchase',
            is_active=True
        ).order_by('subscription_tier', 'min_amount')
        context['purchase_rules'] = purchase_rules
        
        # Правила нарахування балів (за підписки)
        subscription_rules = PointEarningRule.objects.filter(
            rule_type='subscription',
            is_active=True
        ).order_by('subscription_tier', 'subscription_duration_months')
        context['subscription_rules'] = subscription_rules
        
        # Варіанти витрати балів
        redemption_options = RedemptionOption.objects.filter(
            is_active=True
        ).order_by('display_order', 'points_required')
        context['redemption_options'] = redemption_options
        
        # Legacy tier система
        context['loyalty_tiers'] = LoyaltyTier.objects.filter(
            is_active=True
        ).order_by('points_required')
        
        return context
