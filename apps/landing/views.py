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
        first_name = form.cleaned_data['first_name']
        phone = form.cleaned_data['phone']
        email = form.cleaned_data['email']
        
        # Валідація source - використати тільки валідні значення
        VALID_SOURCES = ['landing', 'hub', 'mentoring', 'subscription']
        source = request.POST.get('source', 'landing')
        if source not in VALID_SOURCES:
            source = 'landing'  # Fallback на default
        
        # Зберегти в базу даних
        lead = LeadSubmission.objects.create(
            first_name=first_name,
            phone=phone,
            email=email,
            source=source,
        )
        
        logger.info(f'Lead submission saved: {lead.id} - {first_name} ({email})')
        
        # Спробувати відправити в SendPulse
        try:
            sendpulse = SendPulseService()
            
            # Мапінг джерел на адресні книги
            addressbook_mapping = {
                'hub': getattr(settings, 'SENDPULSE_ADDRESS_BOOK_ID', 497184),
                'mentoring': getattr(settings, 'SENDPULSE_ADDRESS_BOOK_MENTORING', 497185),
                'subscription': getattr(settings, 'SENDPULSE_ADDRESS_BOOK_SUBSCRIPTION', 497186),
            }
            
            # Для форм з hub, mentoring, subscription використовувати адресні книги
            if source in addressbook_mapping:
                addressbook_id = addressbook_mapping[source]
                success = sendpulse.add_contact_to_addressbook(
                    addressbook_id=int(addressbook_id),
                    email=email,
                    phone=phone,
                    name=first_name,
                    source=source
                )
                if success:
                    lead.sendpulse_synced = True
                    lead.save()
                    logger.info(f'Lead {lead.id} synced to SendPulse addressbook {addressbook_id} (source: {source})')
                else:
                    logger.warning(f'Failed to sync lead {lead.id} to SendPulse addressbook {addressbook_id}')
            else:
                # Для інших джерел використовувати старий метод CRM API
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

