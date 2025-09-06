from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone


class MentoringDirection(models.Model):
    """
    6 основних напрямків ментор-коучінгу Play Vision
    """
    DIRECTION_CHOICES = [
        ('game_intelligence', 'Ігровий інтелект'),
        ('physics', 'Фізика'),
        ('technique', 'Техніка'),
        ('mentality', 'Ментальність'),
        ('lifestyle', 'Життя і побут'),
        ('health', 'Здоров\'я'),
    ]
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    direction_type = models.CharField(max_length=50, choices=DIRECTION_CHOICES, unique=True)
    icon = models.CharField(max_length=50, help_text='Emoji або CSS клас іконки')
    description = models.TextField(help_text='Детальний опис напрямку')
    short_description = models.CharField(max_length=300, help_text='Короткий опис для карток')
    
    # Кольорова схема
    primary_color = models.CharField(max_length=7, default='#ff6b35', help_text='Основний колір у hex')
    accent_color = models.CharField(max_length=7, default='#ffffff', help_text='Акцентний колір у hex')
    
    # Позиція в схемі
    position_order = models.PositiveIntegerField(unique=True, help_text='Порядок відображення в колі')
    
    # Налаштування
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Медіа
    image = models.ImageField(upload_to='mentoring/directions/', blank=True)
    background_image = models.ImageField(upload_to='mentoring/backgrounds/', blank=True)
    
    # Метадані
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mentoring_directions'
        verbose_name = 'Mentoring Direction'
        verbose_name_plural = 'Mentoring Directions'
        ordering = ['position_order']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class MentoringProgram(models.Model):
    """
    Програми ментор-коучінгу в рамках напрямків
    """
    PROGRAM_TYPES = [
        ('individual', 'Індивідуальна'),
        ('group', 'Групова'),
        ('intensive', 'Інтенсив'),
        ('course', 'Курс'),
        ('workshop', 'Майстер-клас'),
    ]
    
    DURATION_TYPES = [
        ('session', 'Разова сесія'),
        ('weekly', 'Тижнева програма'),
        ('monthly', 'Місячна програма'),
        ('quarterly', '3-місячна програма'),
        ('ongoing', 'Постійний супровід'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    direction = models.ForeignKey(MentoringDirection, on_delete=models.CASCADE, 
                                related_name='programs')
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPES)
    duration_type = models.CharField(max_length=20, choices=DURATION_TYPES)
    
    # Опис
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    objectives = models.JSONField(default=list, help_text='Список цілей програми')
    methods = models.JSONField(default=list, help_text='Методи роботи')
    
    # Параметри програми
    max_participants = models.PositiveIntegerField(default=1, 
                                                 help_text='Максимальна кількість учасників')
    duration_weeks = models.PositiveIntegerField(default=1, 
                                               help_text='Тривалість у тижнях')
    sessions_per_week = models.PositiveIntegerField(default=1)
    session_duration_minutes = models.PositiveIntegerField(default=60)
    
    # Ціна
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_session = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Вимоги
    min_age = models.PositiveIntegerField(null=True, blank=True)
    max_age = models.PositiveIntegerField(null=True, blank=True)
    skill_level = models.CharField(max_length=50, blank=True, 
                                 help_text='Початковий, середній, професійний')
    prerequisites = models.TextField(blank=True, help_text='Передумови для участі')
    
    # Доступність
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    available_from = models.DateTimeField(default=timezone.now)
    available_until = models.DateTimeField(null=True, blank=True)
    
    # Медіа
    thumbnail = models.ImageField(upload_to='mentoring/programs/', blank=True)
    
    # Метадані
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mentoring_programs'
        verbose_name = 'Mentoring Program'
        verbose_name_plural = 'Mentoring Programs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.direction.name})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def total_sessions(self):
        """Загальна кількість сесій у програмі"""
        return self.duration_weeks * self.sessions_per_week
    
    @property
    def total_duration_hours(self):
        """Загальна тривалість програми в годинах"""
        return (self.total_sessions * self.session_duration_minutes) / 60


class MentoringMentor(models.Model):
    """
    Ментори та коучі
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='mentor_profile')
    
    # Професійна інформація
    title = models.CharField(max_length=100, help_text='Професійна посада')
    bio = models.TextField(help_text='Біографія та досвід')
    specializations = models.ManyToManyField(MentoringDirection, 
                                           related_name='mentors',
                                           help_text='Напрямки спеціалізації')
    
    # Кваліфікації
    certifications = models.JSONField(default=list, help_text='Список сертифікатів')
    experience_years = models.PositiveIntegerField(default=0)
    languages = models.JSONField(default=list, help_text='Мови спілкування')
    
    # Рейтинг
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    reviews_count = models.PositiveIntegerField(default=0)
    
    # Доступність
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    accepts_new_clients = models.BooleanField(default=True)
    
    # Налаштування роботи
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_session_duration = models.PositiveIntegerField(default=60, 
                                                     help_text='Мінімальна тривалість сесії у хвилинах')
    max_clients_per_month = models.PositiveIntegerField(default=20)
    
    # Контакти
    phone = models.CharField(max_length=20, blank=True)
    telegram = models.CharField(max_length=100, blank=True)
    
    # Медіа
    photo = models.ImageField(upload_to='mentoring/mentors/', blank=True)
    
    # Метадані
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mentoring_mentors'
        verbose_name = 'Mentoring Mentor'
        verbose_name_plural = 'Mentoring Mentors'
        ordering = ['-rating', '-reviews_count']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.title}"


class MentoringSession(models.Model):
    """
    Індивідуальні сесії ментор-коучінгу
    """
    STATUS_CHOICES = [
        ('scheduled', 'Заплановано'),
        ('confirmed', 'Підтверджено'),
        ('in_progress', 'В процесі'),
        ('completed', 'Завершено'),
        ('cancelled', 'Скасовано'),
        ('no_show', 'Не з\'явився'),
    ]
    
    # Основна інформація
    mentor = models.ForeignKey(MentoringMentor, on_delete=models.CASCADE,
                             related_name='sessions')
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='mentoring_sessions')
    program = models.ForeignKey(MentoringProgram, on_delete=models.CASCADE,
                              related_name='sessions', null=True, blank=True)
    
    # Час та місце
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    timezone_name = models.CharField(max_length=50, default='Europe/Kyiv')
    meeting_type = models.CharField(max_length=20, choices=[
        ('online', 'Онлайн'),
        ('offline', 'Офлайн'),
        ('phone', 'Телефон'),
    ], default='online')
    meeting_link = models.URLField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    
    # Статус та оплата
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    payment = models.ForeignKey('payments.Payment', on_delete=models.SET_NULL,
                              null=True, blank=True, related_name='mentoring_sessions')
    
    # Деталі сесії
    topic = models.CharField(max_length=200, blank=True, help_text='Тема сесії')
    client_goals = models.TextField(blank=True, help_text='Цілі клієнта')
    notes = models.TextField(blank=True, help_text='Нотатки ментора')
    homework = models.TextField(blank=True, help_text='Домашнє завдання')
    
    # Результати
    completed_at = models.DateTimeField(null=True, blank=True)
    client_rating = models.PositiveIntegerField(null=True, blank=True, 
                                              help_text='Оцінка клієнта від 1 до 5')
    client_feedback = models.TextField(blank=True)
    mentor_notes = models.TextField(blank=True, help_text='Приватні нотатки ментора')
    
    # Метадані
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mentoring_sessions'
        verbose_name = 'Mentoring Session'
        verbose_name_plural = 'Mentoring Sessions'
        ordering = ['-scheduled_at']
    
    def __str__(self):
        return f"{self.mentor.user.get_full_name()} -> {self.client.get_full_name()} ({self.scheduled_at})"


class MentoringEnrollment(models.Model):
    """
    Записи на програми ментор-коучінгу
    """
    STATUS_CHOICES = [
        ('pending', 'Очікує підтвердження'),
        ('approved', 'Підтверджено'),
        ('active', 'Активно'),
        ('completed', 'Завершено'),
        ('cancelled', 'Скасовано'),
    ]
    
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='mentoring_enrollments')
    program = models.ForeignKey(MentoringProgram, on_delete=models.CASCADE,
                              related_name='enrollments')
    mentor = models.ForeignKey(MentoringMentor, on_delete=models.SET_NULL,
                             null=True, blank=True, related_name='enrollments')
    
    # Статус
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Оплата
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    payment = models.ForeignKey('payments.Payment', on_delete=models.SET_NULL,
                              null=True, blank=True, related_name='mentoring_enrollments')
    
    # Прогрес
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sessions_completed = models.PositiveIntegerField(default=0)
    
    # Дати
    enrolled_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Результати
    final_rating = models.PositiveIntegerField(null=True, blank=True,
                                             help_text='Фінальна оцінка програми')
    feedback = models.TextField(blank=True)
    
    class Meta:
        db_table = 'mentoring_enrollments'
        verbose_name = 'Mentoring Enrollment'
        verbose_name_plural = 'Mentoring Enrollments'
        unique_together = ['client', 'program']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.client.get_full_name()} -> {self.program.title}"