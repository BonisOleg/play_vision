"""
Views для системи підписок
"""
from django.views.generic import TemplateView
from django.utils.translation import get_language
from .models import SubscriptionPlan


class PricingView(TemplateView):
    """
    Сторінка тарифів підписки
    """
    template_name = 'subscriptions/pricing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Отримуємо всі активні тарифи
        plans = SubscriptionPlan.objects.filter(is_active=True).order_by('display_order')
        context['plans'] = plans
        
        # Визначаємо валюту на основі мови
        current_language = get_language()
        context['currency'] = 'uah' if current_language == 'uk' else 'usd'
        context['currency_symbol'] = 'грн' if current_language == 'uk' else '$'
        
        # Періоди для перемикача
        context['periods'] = [
            {'value': 'monthly', 'label': 'Ціна за місяць', 'label_short': '1 міс'},
            {'value': '3_months', 'label': 'Ціна за 3 місяці', 'label_short': '3 міс'},
            {'value': '12_months', 'label': 'Ціна за рік', 'label_short': '12 міс'},
        ]
        
        # SEO метадані
        context['meta_title'] = 'Тарифи Play Vision — Твої знання в одній підписці'
        context['meta_description'] = 'Обирай траєкторію свого розвитку: місяць, квартал або рік. Повний доступ до всіх матеріалів та курсів від провідних експертів.'
        
        return context

