from django.contrib import admin
from django.contrib import messages
import logging
from .models import LeadSubmission
from .services import SendPulseService

logger = logging.getLogger(__name__)


@admin.register(LeadSubmission)
class LeadSubmissionAdmin(admin.ModelAdmin):
    list_display = [
        'first_name',
        'phone',
        'email',
        'source',
        'submitted_at',
        'sendpulse_synced'
    ]
    list_filter = ['source', 'sendpulse_synced', 'submitted_at']
    search_fields = ['first_name', 'phone', 'email']
    readonly_fields = ['submitted_at', 'sendpulse_contact_id']
    date_hierarchy = 'submitted_at'
    
    actions = ['sync_to_sendpulse']
    
    def sync_to_sendpulse(self, request, queryset):
        """Синхронізувати обрані заявки з SendPulse"""
        from django.conf import settings
        
        service = SendPulseService()
        success_count = 0
        error_count = 0
        
        # Мапінг джерел на адресні книги
        addressbook_mapping = {
            'hub': getattr(settings, 'SENDPULSE_ADDRESS_BOOK_ID', 497184),
            'mentoring': getattr(settings, 'SENDPULSE_ADDRESS_BOOK_MENTORING', 497185),
            'subscription': getattr(settings, 'SENDPULSE_ADDRESS_BOOK_SUBSCRIPTION', 497186),
        }
        
        for lead in queryset.filter(sendpulse_synced=False):
            # Валідація даних
            if not lead.email or not lead.phone:
                error_count += 1
                logger.warning(
                    f'Lead {lead.id} skipped: missing email or phone. '
                    f'Email: {lead.email}, Phone: {lead.phone}, Source: {lead.source}'
                )
                continue
            
            try:
                # Для форм з hub, mentoring, subscription використовувати адресні книги
                if lead.source in addressbook_mapping:
                    addressbook_id = addressbook_mapping[lead.source]
                    success = service.add_contact_to_addressbook(
                        addressbook_id=int(addressbook_id),
                        email=lead.email,
                        phone=lead.phone,
                        name=lead.first_name,
                        source=lead.source
                    )
                    
                    if success:
                        lead.sendpulse_synced = True
                        lead.save()
                        success_count += 1
                    else:
                        error_count += 1
                        logger.error(
                            f'Failed to sync lead {lead.id} ({lead.email}) to addressbook {addressbook_id}. '
                            f'Source: {lead.source}, Name: {lead.first_name or "N/A"}'
                        )
                else:
                    # Для інших джерел використовувати старий метод CRM API
                    contact_id = service.add_contact(
                        email=lead.email,
                        phone=lead.phone,
                        variables={
                            'first_name': lead.first_name,
                            'source': 'Landing Page - Форум Футбольних Фахівців'
                        }
                    )
                    
                    if contact_id:
                        lead.sendpulse_synced = True
                        # Зберегти contact_id тільки якщо це не маркер 'existing'
                        if contact_id != 'existing':
                            lead.sendpulse_contact_id = contact_id
                        lead.save()
                        success_count += 1
                    else:
                        error_count += 1
                        logger.error(
                            f'Failed to sync lead {lead.id} ({lead.email}) to SendPulse CRM. '
                            f'Source: {lead.source}, Name: {lead.first_name or "N/A"}'
                        )
            except Exception as e:
                error_count += 1
                logger.error(
                    f'Failed to sync lead {lead.id} ({lead.email}): {str(e)}',
                    exc_info=True
                )
                self.message_user(
                    request,
                    f'Помилка синхронізації {lead.first_name or lead.email}: {str(e)}',
                    level=messages.ERROR
                )
        
        if success_count > 0:
            self.message_user(
                request,
                f'Успішно синхронізовано {success_count} заявок з SendPulse',
                level=messages.SUCCESS
            )
        
        if error_count > 0:
            self.message_user(
                request,
                f'Не вдалося синхронізувати {error_count} заявок',
                level=messages.WARNING
            )
    
    sync_to_sendpulse.short_description = 'Синхронізувати з SendPulse CRM'

