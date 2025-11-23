"""
HTMX views for subscriptions
Partial templates for navigation without full page reload
"""
from django.views.generic import TemplateView


class HTMXPricingView(TemplateView):
    """HTMX partial для pricing page"""
    template_name = 'htmx/subscriptions/pricing_content.html'

