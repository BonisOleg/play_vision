from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
















class HeroSlide(models.Model):
    """Hero carousel slides with UA/World dual content"""
    # Ukraine version (primary)
    title_ua = models.CharField('Title (Ukraine)', max_length=200)
    subtitle_ua = models.CharField('Subtitle (Ukraine)', max_length=300, blank=True)
    cta_text_ua = models.CharField('CTA Text (Ukraine)', max_length=50, blank=True)
    
    # World version (fallback)
    title_world = models.CharField('Title (World)', max_length=200, blank=True,
                                   help_text='Leave blank to use Ukraine version worldwide')
    subtitle_world = models.CharField('Subtitle (World)', max_length=300, blank=True)
    cta_text_world = models.CharField('CTA Text (World)', max_length=50, blank=True)
    
    badge = models.CharField('Badge', max_length=50, blank=True, 
                            help_text='Badge text (e.g. "NEW", "TRENDING")')
    
    # Media (shared between versions)
    image = models.ImageField('Image', upload_to='cms/hero/', blank=True,
                             max_length=500, help_text='Recommended: 1920×1080 px')
    video = models.FileField('Video', upload_to='cms/hero/videos/', blank=True,
                            max_length=500, help_text='MP4 format')
    
    # CTA URL (shared)
    cta_url = models.CharField('CTA URL', max_length=200, blank=True)
    
    # Display
    order = models.PositiveIntegerField('Order', default=0,
                                       help_text='Position in carousel (1-7)')
    is_active = models.BooleanField('Active', default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_hero_slides'
        verbose_name = 'Hero Слайд'
        verbose_name_plural = '🏠 Головна → Hero блок'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.title_ua} (#{self.order})"
    
    def get_title(self, country_code='UA'):
        """Get title by country with fallback"""
        if country_code == 'UA' or not self.title_world:
            return self.title_ua
        return self.title_world
    
    def get_subtitle(self, country_code='UA'):
        """Get subtitle by country with fallback"""
        if country_code == 'UA' or not self.subtitle_world:
            return self.subtitle_ua
        return self.subtitle_world
    
    def get_cta_text(self, country_code='UA'):
        """Get CTA text by country with fallback"""
        if country_code == 'UA' or not self.cta_text_world:
            return self.cta_text_ua
        return self.cta_text_world
    
    def save(self, *args, **kwargs):
        """Save slide - Cloudinary optimizes automatically"""
        super().save(*args, **kwargs)






class ExpertCard(models.Model):
    """Expert cards"""
    name = models.CharField('Ім\'я', max_length=100)
    position = models.CharField('Посада', max_length=150)
    specialization = models.CharField('Спеціалізація', max_length=200, blank=True)
    bio = models.TextField('Біографія', blank=True)
    
    photo = models.ImageField('Фото', upload_to='cms/experts/', blank=True,
                             max_length=500, help_text='Рекомендований розмір: 400×400 px')
    
    # Display - per page visibility
    show_on_home = models.BooleanField('Показувати на головній', default=False)
    show_on_about = models.BooleanField('Показувати на "Про нас"', default=False)
    show_on_mentoring = models.BooleanField('Показувати на "Ментор коучинг"', default=False)
    
    # Ordering per page
    order_home = models.PositiveIntegerField('Порядок на головній', default=0)
    order_about = models.PositiveIntegerField('Порядок на "Про нас"', default=0)
    order_mentoring = models.PositiveIntegerField('Порядок на "Ментор коучинг"', default=0)
    
    # General display
    order = models.PositiveIntegerField('Порядок', default=0)  # для сумісності
    is_active = models.BooleanField('Активний', default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_expert_cards'
        verbose_name = 'Спеціаліст'
        verbose_name_plural = 'Команда (використовується скрізь)'
        ordering = ['order_home', 'order_about', 'order_mentoring']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Save expert - Cloudinary optimizes automatically"""
        super().save(*args, **kwargs)




class FeaturedCourse(models.Model):
    """
    Featured courses for homepage carousel (7-12 courses)
    """
    course = models.ForeignKey(
        'content.Course',
        on_delete=models.CASCADE,
        verbose_name='Курс',
        help_text='Курс для відображення (home/hub)'
    )
    page = models.CharField(
        'Сторінка',
        max_length=50,
        default='home',
        db_index=True,
        help_text='На якій сторінці відображати (home, hub тощо)'
    )
    order = models.PositiveIntegerField(
        'Порядок',
        help_text='Порядок відображення (1-12)'
    )
    is_active = models.BooleanField('Активний', default=True, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_featured_courses'
        verbose_name = 'Курс'
        verbose_name_plural = 'Featured Courses'
        ordering = ['page', 'order']
        unique_together = [('page', 'order'), ('page', 'course')]
        indexes = [
            models.Index(fields=['page', 'is_active', 'order']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(order__gte=1) & models.Q(order__lte=12),
                name='featured_course_order_range'
            ),
        ]
    
    def __str__(self):
        return f"{self.page}: {self.course.title} (#{self.order})"


class FeaturedCourseHome(FeaturedCourse):
    """Proxy model for home page featured courses"""
    class Meta:
        proxy = True
        verbose_name = 'Курс'
        verbose_name_plural = '🏠 Головна → Основні програми'


class FeaturedCourseHub(FeaturedCourse):
    """Proxy model for hub page featured courses"""
    class Meta:
        proxy = True
        verbose_name = 'Курс'
        verbose_name_plural = '🎓 Хаб знань → Найпопулярніші продукти'


class EventGridCell(models.Model):
    """
    Grid cells for events hero section (9 cells with GIF/images)
    """
    position = models.PositiveIntegerField(
        'Позиція',
        unique=True,
        help_text='Позиція в сітці (1-9): 1=верх зліва, 9=низ справа'
    )
    image = models.ImageField(
        'Зображення/GIF',
        upload_to='cms/event_grid/',
        max_length=500,
        help_text='Зображення або GIF для комірки'
    )
    alt_text = models.CharField(
        'Alt текст',
        max_length=200,
        blank=True,
        help_text='Опис зображення для доступності'
    )
    is_active = models.BooleanField('Активний', default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_event_grid_cells'
        verbose_name = 'Комірка сітки'
        verbose_name_plural = '🎉 Івенти → Hero сітка'
        ordering = ['position']
        constraints = [
            models.CheckConstraint(
                check=models.Q(position__gte=1) & models.Q(position__lte=9),
                name='event_grid_cell_position_range'
            ),
        ]
    
    def __str__(self):
        return f"Position {self.position}"


class TrackingPixel(models.Model):
    """
    Tracking pixels for Facebook and Google Analytics
    """
    PIXEL_TYPES = [
        ('facebook', 'Facebook Pixel'),
        ('google_analytics', 'Google Analytics'),
        ('google_tag_manager', 'Google Tag Manager'),
        ('custom', 'Custom Pixel'),
    ]
    
    PLACEMENT_CHOICES = [
        ('head', 'Head Section'),
        ('body_start', 'Body Start'),
        ('body_end', 'Body End'),
    ]
    
    name = models.CharField(
        'Назва',
        max_length=100,
        help_text='Описова назва пікселя'
    )
    pixel_type = models.CharField(
        'Тип пікселя',
        max_length=30,
        choices=PIXEL_TYPES
    )
    pixel_id = models.CharField(
        'ID пікселя',
        max_length=100,
        help_text='FB Pixel ID, GA Measurement ID тощо'
    )
    code_snippet = models.TextField(
        'Код пікселя',
        help_text='Повний код для вставки в template'
    )
    placement = models.CharField(
        'Розташування',
        max_length=20,
        choices=PLACEMENT_CHOICES,
        default='head',
        help_text='Де розмістити код'
    )
    is_active = models.BooleanField('Активний', default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_tracking_pixels'
        verbose_name = 'Tracking Pixel'
        verbose_name_plural = '📊 Pixel → Tracking Pixels'
        ordering = ['-created_at']
        unique_together = [('pixel_type', 'pixel_id')]
    
    def __str__(self):
        return f"{self.name} ({self.get_pixel_type_display()})"


class SiteSettings(models.Model):
    """
    Глобальні налаштування сайту (Singleton)
    """
    external_auth_url = models.URLField(
        default='#',
        verbose_name='URL зовнішньої авторизації',
        help_text='Посилання на зовнішній сайт для входу/реєстрації (наприклад, Квіга)'
    )
    
    # Додаткові посилання
    external_join_url_default = models.URLField(
        blank=True,
        verbose_name='URL "Приєднатись" за замовчуванням',
        help_text='Використовується якщо не вказано в курсі'
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_site_settings'
        verbose_name = 'Налаштування сайту'
        verbose_name_plural = 'Налаштування сайту'
    
    def __str__(self):
        return "Налаштування сайту"
    
    def save(self, *args, **kwargs):
        # Singleton - тільки один запис
        self.pk = 1
        super().save(*args, **kwargs)
        # Очистити кеш
        cache.delete('site_settings')
    
    @classmethod
    def get_settings(cls):
        """Отримати налаштування з кешем"""
        settings = cache.get('site_settings')
        if not settings:
            settings, _ = cls.objects.get_or_create(pk=1)
            cache.set('site_settings', settings, 60*60*24)  # 24 години
        return settings


# Import моделей для різних сторінок
from .models_about import AboutHero, AboutSection2, AboutSection3, AboutSection4
from .models_hub import HubHero
from .models_mentor import (
    MentorHero,
    MentorSection1Image,
    MentorSection2,
    MentorSection3,
    MentorSection4,
    MentorCoachingSVG
)

__all__ = [
    # Основні CMS моделі
    'HeroSlide', 'FeaturedCourse', 'FeaturedCourseHome', 'FeaturedCourseHub', 'ExpertCard', 'EventGridCell', 'TrackingPixel', 'SiteSettings',
    # Про нас
    'AboutHero', 'AboutSection2', 'AboutSection3', 'AboutSection4',
    # Хаб знань
    'HubHero',
    # Ментор коучинг
    'MentorHero', 'MentorSection1Image', 'MentorSection2', 'MentorSection3', 'MentorSection4',
    # Ментор на головній
    'MentorCoachingSVG',
]


# Signals для автоматичного очищення кешу при зміні CMS даних
@receiver([post_save, post_delete], sender=HeroSlide)
def clear_hero_slides_cache(sender, **kwargs):
    """Очистити кеш hero slides при додаванні/зміні/видаленні"""
    cache.delete('cms_hero_slides')


@receiver([post_save, post_delete], sender=ExpertCard)
def clear_expert_cards_cache(sender, **kwargs):
    """Очистити кеш експертів при додаванні/зміні/видаленні"""
    cache.delete('cms_experts')  # Backward compatibility
    cache.delete('cms_experts_home')
    cache.delete('cms_experts_about')
    cache.delete('cms_experts_mentoring')


@receiver([post_save, post_delete], sender=FeaturedCourse)
def clear_featured_courses_cache(sender, **kwargs):
    """Очистити кеш featured courses при додаванні/зміні/видаленні"""
    cache.delete('cms_main_courses')