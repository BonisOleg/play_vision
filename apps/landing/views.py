from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
import logging

from .forms import LeadForm
from .models import LeadSubmission
from .services import SendPulseService

logger = logging.getLogger(__name__)


@require_GET
def landing_page(request):
    """Відобразити landing page"""
    context = {
        'form': LeadForm(),
    }
    return render(request, 'landing/landing.html', context)


@require_POST
@csrf_protect
def submit_lead(request):
    """
    Обробка відправки форми заявки
    
    Повертає JSON відповідь:
    - success: True/False
    - message: Повідомлення для користувача
    - errors: Словник помилок валідації (якщо є)
    """
    form = LeadForm(request.POST)
    
    if not form.is_valid():
        return JsonResponse({
            'success': False,
            'message': 'Будь ласка, виправте помилки у формі',
            'errors': form.errors,
        }, status=400)
    
    try:
        # Отримати очищені дані
        full_name = form.cleaned_data['full_name']
        phone = form.cleaned_data['phone']
        email = form.cleaned_data['email']
        promo_code = form.cleaned_data.get('promo_code', '')
        
        # Зберегти в базу даних
        lead = LeadSubmission.objects.create(
            full_name=full_name,
            phone=phone,
            email=email,
            promo_code=promo_code,
        )
        
        logger.info(f'Lead submission saved: {lead.id} - {full_name} ({email})')
        
        # Спробувати відправити в SendPulse CRM
        try:
            sendpulse = SendPulseService()
            contact_id = sendpulse.add_contact(
                email=email,
                phone=phone,
                variables={
                    'full_name': full_name,
                    'promo_code': promo_code,
                    'source': 'Landing Page - Форум Футбольних Фахівців',
                    'discount': '15%',
                }
            )
            
            if contact_id:
                lead.sendpulse_synced = True
                lead.sendpulse_contact_id = contact_id
                lead.save()
                logger.info(f'Lead synced to SendPulse: {contact_id}')
            else:
                logger.warning(f'Failed to sync lead {lead.id} to SendPulse')
                
        except Exception as e:
            # Не падати якщо SendPulse не працює
            logger.error(f'SendPulse sync error for lead {lead.id}: {str(e)}')
        
        # Повернути успішну відповідь
        return JsonResponse({
            'success': True,
            'message': 'Дякуємо! Ваша заявка прийнята. Очікуйте на дзвінок від нашого менеджера.',
        })
        
    except Exception as e:
        logger.error(f'Error processing lead submission: {str(e)}', exc_info=True)
        return JsonResponse({
            'success': False,
            'message': 'Виникла помилка при обробці заявки. Спробуйте ще раз пізніше.',
        }, status=500)

