from django.contrib import admin
from django.contrib import messages
from .models import LeadSubmission
from .services import SendPulseService


@admin.register(LeadSubmission)
class LeadSubmissionAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'phone',
        'email',
        'promo_code',
        'submitted_at',
        'sendpulse_synced'
    ]
    list_filter = ['sendpulse_synced', 'submitted_at']
    search_fields = ['full_name', 'phone', 'email', 'promo_code']
    readonly_fields = ['submitted_at', 'sendpulse_contact_id']
    date_hierarchy = 'submitted_at'
    
    actions = ['sync_to_sendpulse']
    
    def sync_to_sendpulse(self, request, queryset):
        """Синхронізувати обрані заявки з SendPulse CRM"""
        service = SendPulseService()
        success_count = 0
        error_count = 0
        
        for lead in queryset.filter(sendpulse_synced=False):
            try:
                contact_id = service.add_contact(
                    email=lead.email,
                    phone=lead.phone,
                    variables={
                        'full_name': lead.full_name,
                        'promo_code': lead.promo_code,
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
                    f'Помилка синхронізації {lead.full_name}: {str(e)}',
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

