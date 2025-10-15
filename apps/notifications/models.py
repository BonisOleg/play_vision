from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class NotificationTemplate(models.Model):
    """
    Шаблони для різних типів сповіщень
    """
    NOTIFICATION_TYPES = [
        ('welcome', 'Привітання нового користувача'),
        ('survey_reminder', 'Нагадування про анкету'),
        ('course_purchased', 'Курс придбано'),
        ('subscription_activated', 'Підписка активована'),
        ('subscription_expires', 'Підписка закінчується'),
        ('event_reminder', 'Нагадування про івент'),
        ('mentoring_scheduled', 'Ментор-сесія заплановано'),
        ('payment_successful', 'Успішна оплата'),
        ('payment_failed', 'Помилка оплати'),
        ('tier_upgrade', 'Підвищення рівня лояльності'),
    ]
    
    CHANNELS = [
        ('email', 'Email'),
        ('push', 'Push-сповіщення'),
        ('sms', 'SMS'),
        ('in_app', 'В додатку'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    channel = models.CharField(max_length=20, choices=CHANNELS)
    
    # Шаблони
    subject_template = models.CharField(max_length=200, help_text='Тема (для email) або заголовок')
    content_template = models.TextField(help_text='Основний контент з плейсхолдерами')
    html_template = models.TextField(blank=True, help_text='HTML версія для email')
    
    # Налаштування
    is_active = models.BooleanField(default=True)
    is_required = models.BooleanField(default=False, help_text='Обов\'язкове сповіщення')
    delay_minutes = models.PositiveIntegerField(default=0, help_text='Затримка перед відправкою')
    
    # Персоналізація
    use_user_timezone = models.BooleanField(default=True)
    variables = models.JSONField(default=list, help_text='Доступні змінні для шаблону')
    
    # Метадані
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_templates'
        verbose_name = 'Notification Template'
        verbose_name_plural = 'Notification Templates'
        unique_together = ['notification_type', 'channel']
    
    def __str__(self):
        return f"{self.name} ({self.channel})"


class PushSubscription(models.Model):
    """
    Підписки користувачів на push-сповіщення
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                           related_name='push_subscriptions')
    
    # Web Push параметри
    endpoint = models.URLField(help_text='Push endpoint URL')
    p256dh = models.CharField(max_length=200, help_text='P256DH ключ')
    auth = models.CharField(max_length=200, help_text='Auth ключ')
    
    # Метадані браузера/пристрою
    user_agent = models.TextField(blank=True)
    browser = models.CharField(max_length=50, blank=True)
    device_type = models.CharField(max_length=20, choices=[
        ('desktop', 'Desktop'),
        ('mobile', 'Mobile'),
        ('tablet', 'Tablet'),
    ], blank=True)
    
    # Статус
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(null=True, blank=True)
    error_count = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True)
    
    # Метадані
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'push_subscriptions'
        verbose_name = 'Push Subscription'
        verbose_name_plural = 'Push Subscriptions'
        unique_together = ['user', 'endpoint']
    
    def __str__(self):
        return f"{self.user.email} - {self.browser}"


class Notification(models.Model):
    """
    Конкретні сповіщення для користувачів
    """
    STATUS_CHOICES = [
        ('pending', 'Очікує відправки'),
        ('sent', 'Відправлено'),
        ('delivered', 'Доставлено'),
        ('read', 'Прочитано'),
        ('failed', 'Помилка'),
        ('cancelled', 'Скасовано'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                           related_name='notifications')
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE,
                               related_name='notifications')
    
    # Контент
    subject = models.CharField(max_length=200)
    content = models.TextField()
    html_content = models.TextField(blank=True)
    
    # Статус
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Цільовий об'єкт (опціонально)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, 
                                   null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Часи
    scheduled_at = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Метадані
    variables = models.JSONField(default=dict, help_text='Змінні для рендерингу')
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    # Метадані
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['scheduled_at', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.subject}"
    
    def mark_sent(self):
        """Позначити як відправлено"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()
    
    def mark_delivered(self):
        """Позначити як доставлено"""
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save()
    
    def mark_read(self):
        """Позначити як прочитано"""
        self.status = 'read'
        self.read_at = timezone.now()
        self.save()


class NotificationPreference(models.Model):
    """
    Налаштування сповіщень користувача
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='notification_preferences')
    
    # Загальні налаштування
    email_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    
    # Типи сповіщень
    marketing_emails = models.BooleanField(default=True)
    course_updates = models.BooleanField(default=True)
    event_reminders = models.BooleanField(default=True)
    mentoring_notifications = models.BooleanField(default=True)
    payment_notifications = models.BooleanField(default=True)
    loyalty_updates = models.BooleanField(default=True)
    
    # Час доставки
    quiet_hours_start = models.TimeField(default='22:00', help_text='Початок тихих годин')
    quiet_hours_end = models.TimeField(default='08:00', help_text='Кінець тихих годин')
    timezone = models.CharField(max_length=50, default='Europe/Kyiv')
    
    # Частота
    digest_frequency = models.CharField(max_length=20, choices=[
        ('never', 'Ніколи'),
        ('daily', 'Щодня'),
        ('weekly', 'Щотижня'),
        ('monthly', 'Щомісяця'),
    ], default='weekly')
    
    # Метадані
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
    
    def __str__(self):
        return f"{self.user.email} preferences"


class EmailCampaign(models.Model):
    """
    Email кампанії для масових розсилок
    """
    STATUS_CHOICES = [
        ('draft', 'Чернетка'),
        ('scheduled', 'Заплановано'),
        ('sending', 'Відправляється'),
        ('sent', 'Відправлено'),
        ('paused', 'Призупинено'),
        ('cancelled', 'Скасовано'),
    ]
    
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    html_content = models.TextField(blank=True)
    
    # Цільова аудиторія
    target_all_users = models.BooleanField(default=False)
    target_subscribers = models.BooleanField(default=False)
    target_inactive_users = models.BooleanField(default=False)
    target_loyalty_tiers = models.JSONField(default=list, help_text='Цільові рівні лояльності')
    
    # Планування
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    
    # Статистика
    total_recipients = models.PositiveIntegerField(default=0)
    sent_count = models.PositiveIntegerField(default=0)
    delivered_count = models.PositiveIntegerField(default=0)
    opened_count = models.PositiveIntegerField(default=0)
    clicked_count = models.PositiveIntegerField(default=0)
    
    # Метадані
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='created_campaigns')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'email_campaigns'
        verbose_name = 'Email Campaign'
        verbose_name_plural = 'Email Campaigns'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class NotificationLog(models.Model):
    """
    Лог всіх відправлених сповіщень для аналітики
    """
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE,
                                   related_name='logs')
    event = models.CharField(max_length=50, choices=[
        ('created', 'Створено'),
        ('sent', 'Відправлено'),
        ('delivered', 'Доставлено'),
        ('opened', 'Відкрито'),
        ('clicked', 'Клікнуто'),
        ('failed', 'Помилка'),
    ])
    
    # Деталі
    details = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    
    # Метадані
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notification_logs'
        verbose_name = 'Notification Log'
        verbose_name_plural = 'Notification Logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.notification.id} - {self.event}"


class NewsletterSubscriber(models.Model):
    """
    Підписники на розсилку новин
    """
    STATUS_CHOICES = [
        ('active', 'Активний'),
        ('unsubscribed', 'Відписався'),
        ('bounced', 'Відмова доставки'),
        ('complaint', 'Скарга'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Ім\'я')
    email = models.EmailField(unique=True, verbose_name='Email')
    
    # Зв'язок з користувачем (опціонально)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='newsletter_subscription'
    )
    
    # Статус
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Джерело підписки
    source = models.CharField(max_length=50, default='footer_form', choices=[
        ('footer_form', 'Футер сайту'),
        ('popup', 'Спливаюче вікно'),
        ('checkout', 'Форма оплати'),
        ('registration', 'Реєстрація'),
        ('manual', 'Ручне додавання'),
    ])
    
    # IP та метадані
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Часові мітки
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    last_sent_at = models.DateTimeField(null=True, blank=True, 
                                       verbose_name='Остання розсилка')
    
    # Статистика
    emails_sent = models.PositiveIntegerField(default=0)
    emails_opened = models.PositiveIntegerField(default=0)
    emails_clicked = models.PositiveIntegerField(default=0)
    
    # Метадані
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'newsletter_subscribers'
        verbose_name = 'Підписник розсилки'
        verbose_name_plural = 'Підписники розсилки'
        ordering = ['-subscribed_at']
        indexes = [
            models.Index(fields=['email', 'status']),
            models.Index(fields=['status', 'subscribed_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.email})"
    
    def unsubscribe(self):
        """Відписатися від розсилки"""
        self.status = 'unsubscribed'
        self.unsubscribed_at = timezone.now()
        self.save()