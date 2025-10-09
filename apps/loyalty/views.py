from django.views.generic import TemplateView
from .models import LoyaltyTier


class LoyaltyRulesView(TemplateView):
    """
    Сторінка з правилами програми лояльності
    """
    template_name = 'loyalty/rules.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Всі рівні лояльності
        context['loyalty_tiers'] = LoyaltyTier.objects.filter(
            is_active=True
        ).order_by('points_required')
        
        return context
