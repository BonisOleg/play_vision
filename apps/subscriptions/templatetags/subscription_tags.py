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
        period: 'monthly', '3_months'
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
        period: 'monthly', '3_months'
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
    Повертає список переваг плану (backward compatibility)
    
    Args:
        plan: SubscriptionPlan object
    
    Returns:
        list: Список переваг
    """
    try:
        return plan.get_features('monthly')
    except Exception:
        return []


@register.simple_tag
def get_features_for_period(plan, period='monthly'):
    """
    Повертає список переваг для конкретного періоду
    
    Args:
        plan: SubscriptionPlan object
        period: 'monthly' або '3_months'
    
    Returns:
        list: Список переваг
    """
    try:
        return plan.get_features(period)
    except Exception:
        return []


@register.simple_tag
def get_active_discount(plan, period='monthly'):
    """
    Повертає активну знижку для періоду (відсоток)
    Якщо таймер активний, повертає відсоток знижки, інакше 0
    
    Args:
        plan: SubscriptionPlan object
        period: 'monthly' або '3_months'
    
    Returns:
        int: Відсоток знижки або 0
    """
    try:
        return plan.get_active_discount(period)
    except Exception:
        return 0


@register.simple_tag
def get_discount_percentage(plan, period='monthly', currency='uah'):
    """
    Повертає відсоток знижки для періоду (розраховується автоматично)
    
    Args:
        plan: SubscriptionPlan object
        period: 'monthly' або '3_months'
        currency: 'uah' або 'usd'
    
    Returns:
        int: Відсоток знижки (0-100) або 0
    """
    try:
        return plan.get_discount_percentage(period, currency)
    except Exception:
        return 0


@register.simple_tag
def get_sale_price(plan, period='monthly', currency='uah'):
    """
    Повертає ціну після знижки (sale_price) для періоду
    
    Args:
        plan: SubscriptionPlan object
        period: 'monthly' або '3_months'
        currency: 'uah' або 'usd'
    
    Returns:
        float: Ціна після знижки
    """
    try:
        sale_price = plan.get_sale_price(period, currency)
        return float(sale_price) if sale_price else 0
    except Exception:
        return 0


@register.simple_tag
def get_discount_time_left(plan, period='monthly'):
    """
    Повертає час до закінчення знижки
    
    Args:
        plan: SubscriptionPlan object
        period: 'monthly' або '3_months'
    
    Returns:
        timedelta або None
    """
    try:
        return plan.get_discount_time_left(period)
    except Exception:
        return None


@register.filter
def get_feature(plan, index):
    """
    Повертає конкретну перевагу плану за індексом (DEPRECATED)
    Використовуйте get_features_for_period замість цього тега
    
    Args:
        plan: SubscriptionPlan object
        index: int або str - номер переваги (1-30)
    
    Returns:
        str: Текст переваги або порожній рядок
    """
    try:
        # Конвертувати index в int якщо це рядок
        if isinstance(index, str):
            index = int(index)
        
        # Спробувати отримати з monthly полів (новий формат)
        feature_attr = f'feature_{index}_monthly'
        feature = getattr(plan, feature_attr, '')
        if feature:
            return feature
        
        # Fallback на 3months поля
        feature_attr = f'feature_{index}_3months'
        feature = getattr(plan, feature_attr, '')
        if feature:
            return feature
        
        return ''
    except (ValueError, TypeError, AttributeError):
        return ''


@register.simple_tag
def get_base_price(plan, period, currency='uah'):
    """
    Повертає ціну до знижки (original_price) для періоду
    
    Args:
        plan: SubscriptionPlan object
        period: 'monthly', '3_months'
        currency: 'uah' або 'usd'
    
    Returns:
        float: Ціна до знижки
    """
    try:
        original_price = plan.get_original_price(period, currency)
        return float(original_price) if original_price else 0
    except Exception:
        return 0


@register.simple_tag
def get_discount_amount(plan, period, currency='uah'):
    """
    Повертає суму знижки в грошах для періоду (original_price - sale_price)
    
    Args:
        plan: SubscriptionPlan object
        period: 'monthly', '3_months'
        currency: 'uah' або 'usd'
    
    Returns:
        float: Сума знижки
    """
    try:
        original = plan.get_original_price(period, currency)
        sale = plan.get_sale_price(period, currency)
        
        if original == 0 or sale >= original:
            return 0
        
        return float(original - sale)
    except Exception:
        return 0


@register.simple_tag
def get_checkout_url(plan, period='monthly'):
    """
    Повертає посилання на оплату для плану та періоду
    
    Args:
        plan: SubscriptionPlan object
        period: 'monthly' або '3_months'
    
    Returns:
        str: URL для оплати
    """
    try:
        return plan.get_checkout_url(period) or ''
    except Exception:
        return ''
