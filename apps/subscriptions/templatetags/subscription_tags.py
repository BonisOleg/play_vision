"""
Template tags для підписок
"""
from django import template
from decimal import Decimal

register = template.Library()


@register.simple_tag
def calculate_plan_price(plan, period, currency='uah'):
    """
    Розраховує ціну плану для конкретного періоду та валюти
    
    Args:
        plan: SubscriptionPlan object
        period: 'monthly', '3_months', '12_months'
        currency: 'uah' або 'usd'
    
    Returns:
        Decimal: Розрахована ціна
    """
    try:
        price = plan.calculate_price(period, currency)
        return float(price) if price else 0
    except Exception:
        return 0


@register.simple_tag
def get_monthly_price(plan, period, currency='uah'):
    """
    Розраховує ціну за місяць для періоду
    
    Args:
        plan: SubscriptionPlan object
        period: 'monthly', '3_months', '12_months'
        currency: 'uah' або 'usd'
    
    Returns:
        Decimal: Ціна за місяць
    """
    try:
        monthly_price = plan.get_monthly_price(period, currency)
        return float(monthly_price) if monthly_price else 0
    except Exception:
        return 0


@register.filter
def get_features_list(plan):
    """
    Повертає список переваг плану
    
    Args:
        plan: SubscriptionPlan object
    
    Returns:
        list: Список переваг
    """
    try:
        return plan.get_features()
    except Exception:
        return []


@register.filter
def get_feature(plan, index):
    """
    Повертає конкретну перевагу плану за індексом
    
    Args:
        plan: SubscriptionPlan object
        index: int або str - номер переваги (1-5)
    
    Returns:
        str: Текст переваги або порожній рядок
    """
    try:
        # Конвертувати index в int якщо це рядок (з циклу {% for i in "12345" %})
        if isinstance(index, str):
            index = int(index)
        
        feature_attr = f'feature_{index}'
        return getattr(plan, feature_attr, '') or ''
    except (ValueError, TypeError, AttributeError):
        return ''
