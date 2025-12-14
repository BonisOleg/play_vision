from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.conf import settings
from decimal import Decimal


class Course(models.Model):
    """
    Educational courses
    """
    TARGET_AUDIENCE_CHOICES = [
        ('coach_goalkeeper', 'Тренер воротарів'),
        ('coach_youth', 'Дитячий тренер'),
        ('coach_fitness', 'Тренер ЗФП'),
        ('coach_pro', 'Тренер професійних команд'),
        ('analyst_scout', 'Аналітика і скаутинг'),
        ('management', 'Менеджмент'),
        ('psychology', 'Спортивна психологія'),
        ('nutrition', 'Нутриціологія'),
        ('rehabilitation', 'Реабілітація'),
        ('player', 'Футболіст'),
        ('parent', 'Батько'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    author = models.CharField(max_length=200, blank=True, verbose_name='Автор курсу', help_text='Ім\'я автора/інструктора курсу')
    target_audience = models.JSONField(
        default=list, 
        blank=True,
        verbose_name='Кому підходить',
        help_text='Виберіть цільову аудиторію курсу'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Access control
    is_featured = models.BooleanField(default=False)
    is_free = models.BooleanField(default=False)
    requires_subscription = models.BooleanField(default=True)
    subscription_tiers = models.JSONField(default=list, help_text='List of allowed subscription tiers')
    
    # Media
    thumbnail = models.ImageField(upload_to='course_thumbnails/', max_length=500)
    logo = models.ImageField(
        upload_to='course_logos/',
        blank=True,
        null=True,
        max_length=500,
        verbose_name='Лого курсу',
        help_text='Квадратне лого курсу для відображення на картці (рекомендовано 200x200px)'
    )
    preview_video = models.FileField(upload_to='course_previews/', blank=True, max_length=500)  # NOTE: Залишаємо для backward compatibility
    
    # ===== BUNNY.NET PROMO VIDEO =====
    promo_video_file = models.FileField(
        upload_to='course_promo_temp/',
        blank=True,
        null=True,
        max_length=500,
        verbose_name='Промо-відео (тимчасове)',
        help_text='Завантажте відео - воно автоматично піде на Bunny.net CDN'
    )
    promo_video_bunny_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Bunny Video ID',
        help_text='GUID відео в Bunny.net (заповнюється автоматично)',
        db_index=True
    )
    promo_video_bunny_status = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Bunny статус',
        help_text='Статус обробки відео (0-6)'
    )
    promo_video_thumbnail_url = models.URLField(
        blank=True,
        verbose_name='Thumbnail URL',
        help_text='URL thumbnail з Bunny.net'
    )
    
    # ===== EXTERNAL LINKS =====
    external_join_url = models.URLField(
        blank=True,
        verbose_name='Посилання "Приєднатись"',
        help_text='URL зовнішнього сайту для кнопки "Приєднатись до клубу"'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    
    # Statistics
    view_count = models.PositiveIntegerField(default=0)
    enrollment_count = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=300, blank=True)
    
    # 🏷️ Badges and discounts
    has_discount = models.BooleanField(
        'Знижка активна',
        default=False,
        db_index=True,
        help_text='Активувати знижку для цього курсу'
    )
    discount_percent = models.PositiveIntegerField(
        'Відсоток знижки',
        default=0,
        help_text='Вкажіть відсоток знижки (1-99%)'
    )
    is_top_seller = models.BooleanField(
        'Топ продажів',
        default=False,
        db_index=True,
        help_text='Показати бейдж "Топ продажів"'
    )
    
    class Meta:
        db_table = 'courses'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_published', 'published_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('content:course_detail', kwargs={'slug': self.slug})
    
    def get_target_audience_display(self):
        """Повертає список назв аудиторій"""
        choices_dict = dict(self.TARGET_AUDIENCE_CHOICES)
        return [choices_dict.get(code, code) for code in self.target_audience]
    
    def get_promo_embed_url(self):
        """Отримати embed URL для промо-відео"""
        if not self.promo_video_bunny_id:
            return None
        
        try:
            from apps.video_security.bunny_service import BunnyService
            if BunnyService.is_enabled():
                return BunnyService.get_video_embed_url(self.promo_video_bunny_id)
        except ImportError:
            pass
        return None
    
    def get_discounted_price(self):
        """Обчислити ціну зі знижкою"""
        if self.has_discount and self.discount_percent > 0:
            discount_amount = self.price * (Decimal(self.discount_percent) / Decimal('100'))
            return self.price - discount_amount
        return self.price
    
    def get_old_price(self):
        """Отримати стару ціну (якщо є знижка)"""
        if self.has_discount and self.discount_percent > 0:
            return self.price
        return None


class Material(models.Model):
    """
    Course materials/lessons
    """
    CONTENT_TYPES = [
        ('video', 'Відео'),
        ('pdf', 'PDF'),
        ('article', 'Стаття'),
        ('quiz', 'Тест'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    slug = models.SlugField()
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    order = models.PositiveIntegerField(default=0)
    
    # Content
    video_file = models.FileField(upload_to='materials/videos/', blank=True, max_length=500)
    video_duration_seconds = models.PositiveIntegerField(default=0)
    pdf_file = models.FileField(upload_to='materials/pdfs/', blank=True, max_length=500)
    article_content = models.TextField(blank=True)
    
    # Access
    is_preview = models.BooleanField(default=False, help_text='Available without subscription')
    preview_seconds = models.PositiveIntegerField(default=20, help_text='Preview duration for video')
    preview_percentage = models.PositiveIntegerField(default=10, help_text='Preview percentage for PDF/article')
    
    # Secure Video (нові поля для захищеного відео)
    secure_video_enabled = models.BooleanField(default=False, 
                                             help_text='Використовувати захищену доставку відео')
    s3_video_key = models.CharField(max_length=500, blank=True,
                                  help_text='Ключ відео в S3 bucket')
    video_access_token = models.CharField(max_length=100, blank=True,
                                        help_text='Поточний токен доступу')
    token_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Bunny.net CDN Video
    VIDEO_SOURCE_CHOICES = [
        ('local', 'Локальне зберігання'),
        ('s3', 'AWS S3'),
        ('bunny', 'Bunny.net CDN'),
    ]
    video_source = models.CharField(
        max_length=20,
        choices=VIDEO_SOURCE_CHOICES,
        default='local',
        help_text='Джерело відео',
        db_index=True
    )
    bunny_video_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='GUID відео в Bunny.net',
        db_index=True
    )
    bunny_collection_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='ID колекції в Bunny.net'
    )
    bunny_video_status = models.CharField(
        max_length=20,
        blank=True,
        help_text='Статус обробки відео в Bunny.net (0-6)'
    )
    bunny_thumbnail_url = models.URLField(
        blank=True,
        help_text='URL thumbnail з Bunny.net'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'materials'
        verbose_name = 'Material'
        verbose_name_plural = 'Materials'
        unique_together = ['course', 'slug']
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_video_url(self, user=None):
        """Універсальний метод отримання URL відео"""
        # Bunny.net CDN (пріоритет)
        if self.video_source == 'bunny' and self.bunny_video_id:
            try:
                from apps.video_security.bunny_service import BunnyService
                if BunnyService.is_enabled():
                    # Повертаємо embed URL для iframe
                    return BunnyService.get_video_embed_url(self.bunny_video_id)
            except ImportError:
                pass
        
        # Захищене відео (S3 або інше)
        if self.secure_video_enabled and user:
            try:
                from django.apps import apps
                if apps.is_installed('apps.video_security'):
                    from apps.video_security.services import SecureVideoService
                    return SecureVideoService.get_secure_url(self, user)
            except (ImportError, AttributeError, apps.AppRegistryNotReady):
                pass
        
        # Fallback: локальний файл
        if self.video_file and self.video_file.name:
            return self.video_file.url
        
        return None
    
    def get_video_stream_url(self):
        """Отримати URL для HLS стрімінгу (для нативного плеєра)"""
        if self.video_source == 'bunny' and self.bunny_video_id:
            try:
                from apps.video_security.bunny_service import BunnyService
                if BunnyService.is_enabled():
                    return BunnyService.get_video_stream_url(self.bunny_video_id)
            except ImportError:
                pass
        return None


class UserCourseProgress(models.Model):
    """
    Track user progress in courses
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='user_progress')
    materials_completed = models.ManyToManyField(Material, blank=True, related_name='completed_by')
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'user_course_progress'
        verbose_name = 'User Course Progress'
        verbose_name_plural = 'User Course Progress'
        unique_together = ['user', 'course']
    
    def __str__(self):
        return f"{self.user.email} - {self.course.title} ({self.progress_percentage}%)"
    
    def update_progress(self):
        """Update progress percentage based on completed materials"""
        total_materials = self.course.materials.count()
        if total_materials == 0:
            self.progress_percentage = 0
        else:
            completed_count = self.materials_completed.count()
            self.progress_percentage = (completed_count / total_materials) * 100
        
        if self.progress_percentage >= 100 and not self.completed_at:
            self.completed_at = timezone.now()
        
        self.save()


class Favorite(models.Model):
    """
    User favorite courses
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'favorites'
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        unique_together = ['user', 'course']
    
    def __str__(self):
        return f"{self.user.email} - {self.course.title}"


class MonthlyQuote(models.Model):
    """
    Цитата експерта місяця (показується в Хабі знань)
    """
    expert_name = models.CharField(max_length=100, verbose_name='Імʼя експерта')
    expert_role = models.CharField(max_length=150, verbose_name='Посада/роль')
    expert_photo = models.ImageField(
        upload_to='experts/monthly_quotes/', 
        blank=True,
        max_length=500,
        verbose_name='Фото експерта'
    )
    quote_text = models.TextField(verbose_name='Текст цитати')
    
    # Місяць - завжди перше число місяця
    month = models.DateField(
        unique=True,
        verbose_name='Місяць',
        help_text='Завжди 1-е число місяця (напр. 2025-10-01)'
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name='Активна',
        help_text='Тільки одна цитата може бути активною для поточного місяця'
    )
    
    # Статистика
    views_count = models.PositiveIntegerField(default=0)
    last_displayed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'monthly_quotes'
        verbose_name = 'Цитата місяця'
        verbose_name_plural = 'Цитати місяця'
        ordering = ['-month']
        indexes = [
            models.Index(fields=['-month', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.expert_name} - {self.month.strftime('%B %Y')}"
    
    @classmethod
    def get_current_quote(cls):
        """
        Отримати цитату поточного місяця з кешуванням
        """
        from django.core.cache import cache
        
        cache_key = 'current_monthly_quote'
        quote = cache.get(cache_key)
        
        if not quote:
            today = timezone.now().date()
            current_month_start = today.replace(day=1)
            
            quote = cls.objects.filter(
                month=current_month_start,
                is_active=True
            ).first()
            
            if quote:
                # Кешувати до кінця місяця (31 день max)
                cache.set(cache_key, quote, 60*60*24*31)
                
                # Оновити статистику
                quote.views_count += 1
                quote.last_displayed_at = timezone.now()
                quote.save(update_fields=['views_count', 'last_displayed_at'])
        
        return quote
    
    def save(self, *args, **kwargs):
        # Завжди встановлювати перше число місяця
        if self.month:
            self.month = self.month.replace(day=1)
        super().save(*args, **kwargs)
        
        # Очистити кеш при збереженні
        from django.core.cache import cache
        cache.delete('current_monthly_quote')