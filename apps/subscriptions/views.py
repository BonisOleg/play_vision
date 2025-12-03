"""
Views для системи підписок
"""
from django.views.generic import TemplateView
from django.utils.translation import get_language
from .models import SubscriptionPlan


class PricingView(TemplateView):
    """Pricing page with domain-based template selection"""
    
    def get_template_names(self):
        """Select template based on domain"""
        if getattr(self.request, 'is_com_ua_domain', False):
            return ['subscriptions/pricing.html']  # Landing заглушка
        return ['subscriptions/pricing_full.html']  # Повна версія
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Контекст потрібен тільки для повної версії
        if not getattr(self.request, 'is_com_ua_domain', False):
            # Отримуємо всі активні тарифи
            plans = SubscriptionPlan.objects.filter(is_active=True).order_by('display_order')
            context['plans'] = plans
            
            # Визначаємо валюту на основі мови
            current_language = get_language()
            context['currency'] = 'uah' if current_language == 'uk' else 'usd'
            context['currency_symbol'] = 'грн' if current_language == 'uk' else '$'
            
            # Періоди для перемикача
            context['periods'] = [
                {'value': 'monthly', 'label': 'за місяць', 'label_short': '1 міс'},
                {'value': '3_months', 'label': 'за 3 місяці', 'label_short': '3 міс'},
                {'value': '12_months', 'label': 'за рік', 'label_short': '12 міс'},
            ]
            
            # SEO метадані
            context['meta_title'] = 'Тарифи Play Vision — Твої знання в одній підписці'
            context['meta_description'] = 'Обирай траєкторію свого розвитку: місяць, квартал або рік. Повний доступ до всіх матеріалів та курсів від провідних експертів.'
        
        return context

