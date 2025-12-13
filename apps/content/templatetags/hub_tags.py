from django import template
from urllib.parse import urlencode

register = template.Library()


@register.simple_tag(takes_context=True)
def pagination_url(context, page_num):
    """Generate pagination URL preserving current GET params"""
    request = context['request']
    params = request.GET.copy()
    params['page'] = page_num
    return f"?{urlencode(params, doseq=True)}"
