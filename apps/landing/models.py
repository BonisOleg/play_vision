from django.db import models
from django.core.validators import RegexValidator


class LeadSubmission(models.Model):
    """Модель для збереження заявок з landing page"""
    
    first_name = models.CharField(
        'Ім\'я',
        max_length=255,
        help_text='Ім\'я учасника'
    )
    
    phone_validator = RegexValidator(
        regex=r'^\+380\d{9}$',
        message='Номер телефону має бути у форматі +380XXXXXXXXX'
    )
    phone = models.CharField(
        'Телефон',
        max_length=20,
        validators=[phone_validator],
        help_text='Український мобільний номер у форматі +380XXXXXXXXX'
    )
    
    email = models.EmailField(
        'Email',
        help_text='Електронна адреса учасника'
    )
    
    promo_code = models.CharField(
        'Промокод',
        max_length=50,
        blank=True,
        default='',
        help_text='Промокод для знижки (необов\'язково)'
    )
    
    submitted_at = models.DateTimeField(
        'Дата подання',
        auto_now_add=True
    )
    
    sendpulse_synced = models.BooleanField(
        'Синхронізовано з SendPulse',
        default=False,
        help_text='Чи відправлено контакт в SendPulse CRM'
    )
    
    sendpulse_contact_id = models.CharField(
        'ID контакту в SendPulse',
        max_length=100,
        blank=True,
        default='',
        help_text='ID контакту в SendPulse CRM'
    )
    
    source = models.CharField(
        'Джерело заявки',
        max_length=50,
        choices=[
            ('landing', 'Landing Page'),
            ('hub', 'Хаб знань'),
            ('mentoring', 'Ментор-коучинг'),
            ('subscription', 'Підписка'),
        ],
        default='landing',
        help_text='Джерело, з якого прийшла заявка'
    )
    
    class Meta:
        verbose_name = 'Заявка з Landing Page'
        verbose_name_plural = 'Заявки з Landing Page'
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f'{self.first_name} - {self.phone} ({self.submitted_at.strftime("%d.%m.%Y %H:%M")})'

