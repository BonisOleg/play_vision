from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import MinValueValidator
import qrcode
from io import BytesIO
from django.core.files import File
import json
import hashlib
import base64


class Event(models.Model):
    """
    Events and seminars
    """
    EVENT_TYPE_CHOICES = [
        ('forum', 'Форум'),
        ('webinar', 'Вебінар'),
        ('workshop', 'Майстер-клас'),
        ('internship', 'Стажування'),
        ('seminar', 'Семінар'),
        ('conference', 'Конференція'),
    ]
    
    EVENT_CATEGORY_CHOICES = [
        ('football_experts_forum', 'Форум футбольних фахівців'),
        ('parents_forum', 'Форум футбольних батьків'),
        ('internships', 'Стажування в професійних клубах'),
        ('seminars_hackathons', 'Практичні семінари і хакатони'),
        ('psychology_workshops', 'Воркшопи зі спортивної психології'),
        ('selection_camps', 'Селекційні табори'),
        ('online_webinars', 'Онлайн-теорії і вебінари'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Чернетка'),
        ('published', 'Опублікований'),
        ('cancelled', 'Скасований'),
        ('completed', 'Завершений'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    event_category = models.CharField(
        max_length=50,
        choices=EVENT_CATEGORY_CHOICES,
        blank=True,
        help_text='Специфічна категорія події для меню'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Dates and location
    start_datetime = models.DateTimeField(blank=True, null=True)
    end_datetime = models.DateTimeField(blank=True, null=True)
    timezone_name = models.CharField(max_length=50, default='Europe/Kyiv')
    location = models.CharField(max_length=200, blank=True, help_text='Фізична адреса або "Онлайн"')
    online_link = models.URLField(blank=True, help_text='Посилання для онлайн івенту')
    
    # Format
    is_online_event = models.BooleanField(
        default=False,
        verbose_name='Онлайн подія',
        help_text='Поставте галочку якщо подія проводиться онлайн'
    )
    
    # Capacity and pricing
    max_attendees = models.PositiveIntegerField(default=100)
    tickets_sold = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    is_free = models.BooleanField(default=False)
    requires_subscription = models.BooleanField(default=False, 
                                              help_text='Чи можна використати квитки з підписки')
    
    # Event details
    benefits = models.JSONField(
        default=list,
        blank=True,
        help_text='Список переваг події (що отримає учасник)',
        verbose_name='Що ти отримаєш'
    )
    
    target_audience = models.JSONField(
        default=list,
        blank=True,
        help_text='Для кого ця подія (цільова аудиторія)',
        verbose_name='Для кого'
    )
    
    ticket_tiers = models.JSONField(
        default=list,
        blank=True,
        help_text='Тарифи квитків: [{"name": "Базовий", "price": 350, "features": ["пункт 1", "..."], "is_popular": false}]',
        verbose_name='Тарифи квитків'
    )
    
    # Media
    thumbnail = models.ImageField(upload_to='event_thumbnails/', blank=True, max_length=500)
    banner_image = models.ImageField(upload_to='event_banners/', blank=True, max_length=500)
    
    # Organization
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                                related_name='organized_events', blank=True, null=True)
    speakers = models.ManyToManyField('Speaker', blank=True, related_name='events')
    experts = models.ManyToManyField(
        'cms.ExpertCard', 
        blank=True, 
        related_name='expert_events',
        verbose_name='Експерти команди',
        help_text='Члени команди Play Vision як спікери'
    )
    
    # Features
    is_featured = models.BooleanField(default=False)
    requires_approval = models.BooleanField(default=False, 
                                          help_text='Чи потрібне підтвердження реєстрації')
    send_reminders = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Архівність
    is_archived = models.BooleanField(
        default=False,
        verbose_name='Архівний івент',
        help_text='Відмітьте якщо подія вже відбулася. Дата/час необов\'язкові для архівних подій'
    )
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=300, blank=True)
    
    class Meta:
        db_table = 'events'
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['start_datetime']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status', 'start_datetime']),
            models.Index(fields=['event_type', 'status']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        super().clean()
        
        # Валідація дат для не-архівних подій
        if not self.is_archived:
            if not self.start_datetime:
                raise ValidationError({
                    'start_datetime': 'Дата початку обов\'язкова для майбутніх подій'
                })
            if self.start_datetime and self.end_datetime:
                if self.end_datetime <= self.start_datetime:
                    raise ValidationError({
                        'end_datetime': 'Дата завершення має бути пізніше дати початку'
                    })
        
        # Валідація тарифів для платних івентів
        if not self.is_free and not self.ticket_tiers:
            raise ValidationError({
                'ticket_tiers': 'Для платних подій потрібно заповнити тарифи квитків'
            })
    
    @property
    def is_truly_free(self):
        """Івент безкоштовний (is_free=True або всі тарифи з ціною 0)"""
        if self.is_free:
            return True
        if self.ticket_tiers:
            return all(tier.get('price', 0) == 0 for tier in self.ticket_tiers)
        return False
    
    @property
    def display_scenario(self):
        """
        Повертає сценарій відображення квитків:
        'paid' - платний (3 тарифи)
        'free_upcoming' - безкоштовний майбутній
        'free_archived' - безкоштовний архівний (без квитків)
        'paid_archived' - платний архівний (без квитків)
        """
        if self.is_archived:
            return 'free_archived' if self.is_truly_free else 'paid_archived'
        return 'free_upcoming' if self.is_truly_free else 'paid'
    
    @property
    def is_online(self):
        """Check if event is online"""
        return self.is_online_event
    
    @property
    def is_upcoming(self):
        """Перевірка чи подія майбутня"""
        if self.is_archived:
            return False
        if not self.start_datetime:
            return False
        return self.start_datetime > timezone.now()
    
    @property
    def is_ongoing(self):
        """Check if event is currently ongoing"""
        now = timezone.now()
        return self.start_datetime <= now <= self.end_datetime
    
    @property
    def is_sold_out(self):
        """Check if event is sold out"""
        return self.tickets_sold >= self.max_attendees
    
    @property
    def available_tickets(self):
        """Get number of available tickets"""
        return max(0, self.max_attendees - self.tickets_sold)
    
    @property
    def duration_minutes(self):
        """Get event duration in minutes"""
        if self.end_datetime and self.start_datetime:
            delta = self.end_datetime - self.start_datetime
            return int(delta.total_seconds() / 60)
        return 0
    
    def can_register(self, user=None):
        """Check if user can register for event"""
        if self.status != 'published':
            return False, "Івент не опублікований"
        
        if not self.is_upcoming:
            return False, "Реєстрація закрита"
        
        if self.is_sold_out:
            return False, "Всі квитки продані"
        
        if user and self.has_user_ticket(user):
            return False, "Ви вже зареєстровані"
        
        return True, ""
    
    def has_user_ticket(self, user):
        """Check if user has ticket for this event"""
        return self.tickets.filter(user=user, status__in=['confirmed', 'used']).exists()
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('events:event_detail', kwargs={'slug': self.slug})


class Speaker(models.Model):
    """
    Event speakers and experts
    """
    first_name = models.CharField(max_length=50, default='')
    last_name = models.CharField(max_length=50, default='')
    email = models.EmailField(unique=True, blank=True, default='')
    bio = models.TextField(default='')
    position = models.CharField(max_length=100)
    company = models.CharField(max_length=100, blank=True)
    
    # Media
    photo = models.ImageField(upload_to='speaker_photos/', blank=True, max_length=500)
    
    # Social links
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    
    # Settings
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'speakers'
        verbose_name = 'Speaker'
        verbose_name_plural = 'Speakers'
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_photo_url(self):
        """Get speaker photo URL or default"""
        if self.photo:
            return self.photo.url
        return '/static/images/default-speaker.png'


class EventTicket(models.Model):
    """
    Event tickets with QR codes
    """
    STATUS_CHOICES = [
        ('pending', 'Очікує оплати'),
        ('confirmed', 'Підтверджений'),
        ('cancelled', 'Скасований'),
        ('used', 'Використаний'),
        ('refunded', 'Повернений'),
    ]
    
    # Core fields
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                           related_name='event_tickets')
    ticket_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, 
                               validators=[MinValueValidator(0)],
                               help_text='Ціна квитка на момент покупки')
    tier_name = models.CharField(max_length=50, blank=True, 
                                 help_text='Назва тарифу (Базовий, ПРО, Преміум)')
    
    # Payment
    payment = models.ForeignKey('payments.Payment', on_delete=models.SET_NULL, 
                              null=True, blank=True, related_name='event_tickets')
    used_balance = models.BooleanField(default=False, 
                                     help_text='Чи використаний баланс квитків з підписки')
    
    # QR Code
    qr_code = models.ImageField(upload_to='ticket_qr/', blank=True, max_length=500)
    qr_data = models.TextField(blank=True, help_text='Дані для QR коду')
    
    # Usage tracking
    used_at = models.DateTimeField(null=True, blank=True)
    checked_in_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='checked_in_tickets')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'event_tickets'
        verbose_name = 'Event Ticket'
        verbose_name_plural = 'Event Tickets'
        unique_together = ['event', 'user']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ticket_number']),
            models.Index(fields=['event', 'status']),
            models.Index(fields=['user', 'status']),
        ]
    
    def __str__(self):
        return f"Ticket #{self.ticket_number} - {self.event.title}"
    
    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = self.generate_ticket_number()
        super().save(*args, **kwargs)
        
        # Generate QR code after save (when we have ID)
        if not self.qr_code:
            self.generate_qr_code()
    
    def generate_ticket_number(self):
        """Generate unique ticket number"""
        import random
        import string
        
        # Обмежуємо кількість спроб для безпеки
        max_attempts = 100
        for attempt in range(max_attempts):
            number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not EventTicket.objects.filter(ticket_number=number).exists():
                return number
        
        # Якщо не змогли згенерувати унікальний номер за 100 спроб
        # використовуємо більш довгий номер з timestamp
        import time
        timestamp_suffix = str(int(time.time()))[-4:]  # Останні 4 цифри timestamp
        number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) + timestamp_suffix
        return number
    
    def generate_qr_code(self):
        """Generate QR code for ticket"""
        # Create QR data
        qr_data = {
            'ticket_id': self.id,
            'event_id': self.event.id,
            'user_id': self.user.id,
            'ticket_number': self.ticket_number,
            'hash': self.generate_secure_hash()
        }
        
        # Encode data
        encoded_data = base64.b64encode(json.dumps(qr_data).encode()).decode()
        self.qr_data = encoded_data
        
        # Generate QR code image
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(encoded_data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to file field
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f'ticket_{self.ticket_number}.png'
        self.qr_code.save(filename, File(buffer), save=False)
        
        # Save model
        EventTicket.objects.filter(id=self.id).update(
            qr_data=self.qr_data,
            qr_code=self.qr_code
        )
    
    def generate_secure_hash(self):
        """Generate secure hash for QR validation"""
        data = f"{self.id}{self.event.id}{self.user.id}{self.ticket_number}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def validate_qr_data(self, qr_data_input):
        """Validate QR code data"""
        try:
            decoded_data = json.loads(base64.b64decode(qr_data_input).decode())
            
            return (
                decoded_data.get('ticket_id') == self.id and
                decoded_data.get('event_id') == self.event.id and
                decoded_data.get('user_id') == self.user.id and
                decoded_data.get('ticket_number') == self.ticket_number and
                decoded_data.get('hash') == self.generate_secure_hash()
            )
        except (json.JSONDecodeError, ValueError):
            return False
    
    def check_in(self, checked_by=None):
        """Check in the ticket"""
        if self.status != 'confirmed':
            return False, "Квиток не підтверджений"
        
        if self.status == 'used':
            return False, f"Квиток вже використаний {self.used_at.strftime('%d.%m.%Y %H:%M')}"
        
        self.status = 'used'
        self.used_at = timezone.now()
        self.checked_in_by = checked_by
        self.save()
        
        return True, "Квиток успішно відмічений"
    
    def cancel(self):
        """Cancel the ticket"""
        if self.status == 'used':
            return False, "Неможливо скасувати використаний квиток"
        
        self.status = 'cancelled'
        self.save()
        
        # Return ticket to event availability
        if self.event.tickets_sold > 0:
            self.event.tickets_sold -= 1
            self.event.save()
        
        return True, "Квиток скасовано"


class EventRegistration(models.Model):
    """
    Additional registration data for events
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                           related_name='event_registrations')
    ticket = models.OneToOneField(EventTicket, on_delete=models.CASCADE, 
                                related_name='registration', null=True, blank=True)
    
    # Attendee information
    attendee_name = models.CharField(max_length=200, default='')
    attendee_email = models.EmailField(blank=True, default='')
    attendee_phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=200, blank=True)
    position = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True, help_text='Очікування від події')
    
    # Additional info
    dietary_requirements = models.TextField(blank=True)
    special_needs = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    
    # Marketing
    how_did_you_hear = models.CharField(max_length=100, blank=True)
    marketing_consent = models.BooleanField(default=False)
    
    # Custom fields (JSON for flexibility)
    custom_fields = models.JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'event_registrations'
        verbose_name = 'Event Registration'
        verbose_name_plural = 'Event Registrations'
    
    def __str__(self):
        return f"Registration for {self.ticket}"


class EventWaitlist(models.Model):
    """
    Waitlist for sold out events
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='waitlist')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                           related_name='event_waitlist')
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    # Status
    notified = models.BooleanField(default=False)
    notified_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'event_waitlist'
        verbose_name = 'Event Waitlist'
        verbose_name_plural = 'Event Waitlists'
        unique_together = ['event', 'user']
        ordering = ['created_at']
    
    def __str__(self):
        return f"Waitlist: {self.user.email} for {self.event.title}"


class EventFeedback(models.Model):
    """
    Post-event feedback
    """
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                           related_name='event_feedback')
    
    # Ratings
    overall_rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    content_rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    speaker_rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    organization_rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    
    # Comments
    what_liked = models.TextField(blank=True)
    what_could_improve = models.TextField(blank=True)
    additional_comments = models.TextField(blank=True)
    
    # Recommendations
    would_recommend = models.BooleanField()
    would_attend_again = models.BooleanField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'event_feedback'
        verbose_name = 'Event Feedback'
        verbose_name_plural = 'Event Feedback'
        unique_together = ['event', 'user']
    
    def __str__(self):
        return f"Feedback for {self.event.title} by {self.user.email}"
