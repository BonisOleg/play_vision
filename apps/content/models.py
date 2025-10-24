from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.conf import settings


class Category(models.Model):
    """
    Course categories
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='CSS class or SVG icon')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    """
    Content tags and user interests
    """
    TAG_TYPE_CHOICES = [
        ('interest', 'Інтерес користувача'),
        ('category', 'Категорія контенту'),
        ('general', 'Загальний тег'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    tag_type = models.CharField(
        max_length=20, 
        choices=TAG_TYPE_CHOICES, 
        default='general',
        db_index=True
    )
    display_order = models.PositiveIntegerField(
        default=0, 
        help_text='Порядок відображення (для interest type)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tags'
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['tag_type', 'display_order']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Course(models.Model):
    """
    Educational courses
    """
    DIFFICULTY_CHOICES = [
        ('beginner', 'Початковий'),
        ('intermediate', 'Середній'),
        ('advanced', 'Експертний'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    author = models.CharField(max_length=200, blank=True, verbose_name='Автор курсу', help_text='Ім\'я автора/інструктора курсу')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')
    tags = models.ManyToManyField(Tag, blank=True, related_name='courses')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    duration_minutes = models.PositiveIntegerField(help_text='Duration in minutes')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Тип контенту (для фільтрації)
    CONTENT_TYPE_CHOICES = [
        ('video', 'Відео'),
        ('pdf', 'PDF документ'),
        ('article', 'Стаття'),
        ('mixed', 'Змішаний'),
    ]
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES,
        default='mixed',
        verbose_name='Тип контенту',
        help_text='Основний тип матеріалів у курсі',
        db_index=True
    )
    
    # Цільова аудиторія (кому підходить)
    TARGET_AUDIENCE_CHOICES = [
        ('player', 'Гравець'),
        ('parent', 'Батьки'),
        ('coach', 'Тренер'),
        ('coach_gk', 'Тренер воротарів'),
        ('coach_youth', 'Дитячий тренер'),
        ('coach_fitness', 'Тренер ЗФП'),
        ('analyst', 'Аналітик'),
        ('scout', 'Скаут'),
        ('psychologist', 'Психологія'),
        ('nutritionist', 'Нутриціологія'),
        ('media', 'Медіа'),
        ('manager', 'Менеджер'),
    ]
    target_audience = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Кому підходить',
        help_text='Список цільових аудиторій (можна обрати декілька)'
    )
    
    # Training specialization
    training_specialization = models.CharField(
        max_length=30,
        choices=[
            ('', 'Загальний'),
            ('goalkeeper', 'Тренер воротарів'),
            ('youth', 'Дитячий тренер'),
            ('fitness', 'Тренер ЗФП'),
            ('professional', 'Тренер професійних команд'),
        ],
        blank=True,
        default='',
        verbose_name='Спеціалізація тренера',
        help_text='Застосовується тільки для курсів категорії "Тренерство"',
        db_index=True
    )
    
    # Access control
    is_featured = models.BooleanField(default=False)
    is_free = models.BooleanField(default=False)
    requires_subscription = models.BooleanField(default=True)
    subscription_tiers = models.JSONField(default=list, help_text='List of allowed subscription tiers')
    
    # Media
    thumbnail = models.ImageField(upload_to='course_thumbnails/')
    preview_video = models.FileField(upload_to='course_previews/', blank=True)
    
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
    
    @property
    def duration_display(self):
        """Get human-readable duration"""
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        if hours:
            return f"{hours}г {minutes}хв"
        return f"{minutes}хв"
    
    def get_target_audience_display(self):
        """Отримати відображувані назви цільової аудиторії"""
        audience_dict = dict(self.TARGET_AUDIENCE_CHOICES)
        if not self.target_audience:
            return []
        return [audience_dict.get(code, code) for code in self.target_audience]
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('content:course_detail', kwargs={'slug': self.slug})


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
    video_file = models.FileField(upload_to='materials/videos/', blank=True)
    video_duration_seconds = models.PositiveIntegerField(default=0)
    pdf_file = models.FileField(upload_to='materials/pdfs/', blank=True)
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
        if self.secure_video_enabled and user:
            # Новий захищений спосіб з безпечним імпортом
            try:
                # Використовуємо пізній імпорт для уникнення циклічного імпорту
                from django.apps import apps
                if apps.is_installed('apps.video_security'):
                    from apps.video_security.services import SecureVideoService
                    return SecureVideoService.get_secure_url(self, user)
            except (ImportError, AttributeError, apps.AppRegistryNotReady):
                # Fallback якщо video_security не встановлений або є проблеми з імпортом
                pass
        
        # Старий спосіб (fallback) для зворотної сумісності
        if self.video_file and self.video_file.name:
            return self.video_file.url
        
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