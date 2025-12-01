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


@require_GET
def hub_lead_form_page(request):
    """Відобразити форму для Хаб знань"""
    return render(request, 'landing/hub_lead_form.html')


@require_GET
def mentoring_lead_form_page(request):
    """Відобразити форму для Ментор коучингу"""
    return render(request, 'landing/mentoring_lead_form.html')


@require_GET
def subscription_lead_form_page(request):
    """Відобразити форму для Підписки"""
    return render(request, 'landing/subscription_lead_form.html')


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
        first_name = form.cleaned_data['first_name']
        phone = form.cleaned_data['phone']
        email = form.cleaned_data['email']
        source = request.POST.get('source', 'landing')
        
        # Зберегти в базу даних
        lead = LeadSubmission.objects.create(
            first_name=first_name,
            phone=phone,
            email=email,
            source=source,
        )
        
        logger.info(f'Lead submission saved: {lead.id} - {first_name} ({email})')
        
        # Спробувати відправити в SendPulse CRM
        try:
            sendpulse = SendPulseService()
            contact_id = sendpulse.add_contact(
                email=email,
                phone=phone,
                variables={
                    'first_name': first_name,
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

