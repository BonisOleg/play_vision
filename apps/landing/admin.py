from django.contrib import admin
from django.contrib import messages
from .models import LeadSubmission
from .services import SendPulseService


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
                        lead.sendpulse_contact_id = contact_id
                        lead.save()
                        success_count += 1
                    else:
                        error_count += 1
            except Exception as e:
                error_count += 1
                self.message_user(
                    request,
                    f'Помилка синхронізації {lead.first_name}: {str(e)}',
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

