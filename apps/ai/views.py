"""
Спрощені views для AI (тільки базові функції)
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View
from .models import AIConfiguration


class AIChatView(TemplateView):
    """Головна сторінка AI чату (заглушка)"""
    template_name = 'ai/chat.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Перевірити чи увімкнений AI
        try:
            config = AIConfiguration.objects.first()
            context['ai_enabled'] = config.is_enabled if config else False
        except:
            context['ai_enabled'] = False
        
        return context
