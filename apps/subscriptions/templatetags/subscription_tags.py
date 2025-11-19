"""
Custom template tags for subscription pricing
"""
from django import template

register = template.Library()


@register.simple_tag
def calculate_plan_price(plan, period, currency):
    """
    Calculate plan price for given period and currency
    
    Usage in template:
        {% calculate_plan_price plan "3_months" currency %}
    """
    try:
        return plan.calculate_price(period, currency)
    except (ValueError, AttributeError):
        return 0


@register.filter
def get_feature(plan, feature_num):
    """
    Get plan feature by number
    
    Usage in template:
        {{ plan|get_feature:1 }}
    """
    try:
        feature_attr = f'feature_{feature_num}'
        return getattr(plan, feature_attr, '')
    except (ValueError, AttributeError):
        return ''

