from django.shortcuts import render
from apps.cms.models import CMSExpert

def mentoring_page(request):
    """
    Сторінка Ментор-коучингу
    """
    # Отримуємо експертів з CMS якщо вони є
    cms_experts = CMSExpert.objects.filter(is_active=True).order_by('order')
    
    context = {
        'cms_experts': cms_experts,
    }
    
    return render(request, 'pages/mentoring.html', context)
