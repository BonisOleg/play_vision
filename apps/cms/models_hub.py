"""
Моделі для сторінки "Хаб знань"
"""
from django.db import models


class HubHero(models.Model):
    """Hero секція для Хаб знань - фон + до 5 заголовків"""
    # Загальне фонове зображення (fallback)
    background_image = models.ImageField('Фонове зображення (загальне)', upload_to='cms/hub/hero/', max_length=500, blank=True, help_text='Використовується як fallback, якщо для слайда не вказано окремий бекграунд')
    
    # Заголовок 1 (UA/World)
    title_1_ua = models.CharField('Заголовок 1 (Україна)', max_length=200)
    subtitle_1_ua = models.CharField('Підзаголовок 1 (Україна)', max_length=300, blank=True)
    title_1_world = models.CharField('Заголовок 1 (Світ)', max_length=200, blank=True)
    subtitle_1_world = models.CharField('Підзаголовок 1 (Світ)', max_length=300, blank=True)
    background_image_1 = models.ImageField('Бекграунд зображення 1', upload_to='cms/hub/hero/', max_length=500, blank=True, help_text='Рекомендовано: 1920×1080 px')
    background_video_1 = models.FileField('Бекграунд відео 1', upload_to='cms/hub/hero/videos/', max_length=500, blank=True, help_text='MP4 формат')
    cta_text_1_ua = models.CharField('CTA текст 1 (Україна)', max_length=50, blank=True)
    cta_text_1_world = models.CharField('CTA текст 1 (Світ)', max_length=50, blank=True)
    cta_url_1 = models.CharField('CTA URL 1', max_length=200, blank=True)
    
    # Заголовок 2 (UA/World)
    title_2_ua = models.CharField('Заголовок 2 (Україна)', max_length=200, blank=True)
    subtitle_2_ua = models.CharField('Підзаголовок 2 (Україна)', max_length=300, blank=True)
    title_2_world = models.CharField('Заголовок 2 (Світ)', max_length=200, blank=True)
    subtitle_2_world = models.CharField('Підзаголовок 2 (Світ)', max_length=300, blank=True)
    background_image_2 = models.ImageField('Бекграунд зображення 2', upload_to='cms/hub/hero/', max_length=500, blank=True, help_text='Рекомендовано: 1920×1080 px')
    background_video_2 = models.FileField('Бекграунд відео 2', upload_to='cms/hub/hero/videos/', max_length=500, blank=True, help_text='MP4 формат')
    cta_text_2_ua = models.CharField('CTA текст 2 (Україна)', max_length=50, blank=True)
    cta_text_2_world = models.CharField('CTA текст 2 (Світ)', max_length=50, blank=True)
    cta_url_2 = models.CharField('CTA URL 2', max_length=200, blank=True)
    
    # Заголовок 3 (UA/World)
    title_3_ua = models.CharField('Заголовок 3 (Україна)', max_length=200, blank=True)
    subtitle_3_ua = models.CharField('Підзаголовок 3 (Україна)', max_length=300, blank=True)
    title_3_world = models.CharField('Заголовок 3 (Світ)', max_length=200, blank=True)
    subtitle_3_world = models.CharField('Підзаголовок 3 (Світ)', max_length=300, blank=True)
    background_image_3 = models.ImageField('Бекграунд зображення 3', upload_to='cms/hub/hero/', max_length=500, blank=True, help_text='Рекомендовано: 1920×1080 px')
    background_video_3 = models.FileField('Бекграунд відео 3', upload_to='cms/hub/hero/videos/', max_length=500, blank=True, help_text='MP4 формат')
    cta_text_3_ua = models.CharField('CTA текст 3 (Україна)', max_length=50, blank=True)
    cta_text_3_world = models.CharField('CTA текст 3 (Світ)', max_length=50, blank=True)
    cta_url_3 = models.CharField('CTA URL 3', max_length=200, blank=True)
    
    # Заголовок 4 (UA/World)
    title_4_ua = models.CharField('Заголовок 4 (Україна)', max_length=200, blank=True)
    subtitle_4_ua = models.CharField('Підзаголовок 4 (Україна)', max_length=300, blank=True)
    title_4_world = models.CharField('Заголовок 4 (Світ)', max_length=200, blank=True)
    subtitle_4_world = models.CharField('Підзаголовок 4 (Світ)', max_length=300, blank=True)
    background_image_4 = models.ImageField('Бекграунд зображення 4', upload_to='cms/hub/hero/', max_length=500, blank=True, help_text='Рекомендовано: 1920×1080 px')
    background_video_4 = models.FileField('Бекграунд відео 4', upload_to='cms/hub/hero/videos/', max_length=500, blank=True, help_text='MP4 формат')
    cta_text_4_ua = models.CharField('CTA текст 4 (Україна)', max_length=50, blank=True)
    cta_text_4_world = models.CharField('CTA текст 4 (Світ)', max_length=50, blank=True)
    cta_url_4 = models.CharField('CTA URL 4', max_length=200, blank=True)
    
    # Заголовок 5 (UA/World)
    title_5_ua = models.CharField('Заголовок 5 (Україна)', max_length=200, blank=True)
    subtitle_5_ua = models.CharField('Підзаголовок 5 (Україна)', max_length=300, blank=True)
    title_5_world = models.CharField('Заголовок 5 (Світ)', max_length=200, blank=True)
    subtitle_5_world = models.CharField('Підзаголовок 5 (Світ)', max_length=300, blank=True)
    background_image_5 = models.ImageField('Бекграунд зображення 5', upload_to='cms/hub/hero/', max_length=500, blank=True, help_text='Рекомендовано: 1920×1080 px')
    background_video_5 = models.FileField('Бекграунд відео 5', upload_to='cms/hub/hero/videos/', max_length=500, blank=True, help_text='MP4 формат')
    cta_text_5_ua = models.CharField('CTA текст 5 (Україна)', max_length=50, blank=True)
    cta_text_5_world = models.CharField('CTA текст 5 (Світ)', max_length=50, blank=True)
    cta_url_5 = models.CharField('CTA URL 5', max_length=200, blank=True)
    
    is_active = models.BooleanField('Активно', default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_hub_hero'
        verbose_name = 'Hero секція'
        verbose_name_plural = '🎓 Хаб знань → Hero секція'
    
    def __str__(self):
        return "Hero - Хаб знань"
    
    def get_title(self, number, country_code='UA'):
        """Отримати заголовок по номеру (1-5) та країні"""
        field_name = f"title_{number}_{'world' if country_code != 'UA' else 'ua'}"
        title = getattr(self, field_name, '')
        
        # Fallback до UA
        if not title and country_code != 'UA':
            title = getattr(self, f"title_{number}_ua", '')
        
        return title
    
    def get_subtitle(self, number, country_code='UA'):
        """Отримати підзаголовок по номеру (1-5) та країні"""
        field_name = f"subtitle_{number}_{'world' if country_code != 'UA' else 'ua'}"
        subtitle = getattr(self, field_name, '')
        
        # Fallback до UA
        if not subtitle and country_code != 'UA':
            subtitle = getattr(self, f"subtitle_{number}_ua", '')
        
        return subtitle
    
    def get_background_image(self, number):
        """Отримати бекграунд зображення для слайда (1-5)"""
        field_name = f"background_image_{number}"
        image = getattr(self, field_name, None)
        # Fallback до загального background_image
        if not image:
            return self.background_image
        return image
    
    def get_background_video(self, number):
        """Отримати бекграунд відео для слайда (1-5)"""
        field_name = f"background_video_{number}"
        return getattr(self, field_name, None)
    
    def get_cta_text(self, number, country_code='UA'):
        """Отримати CTA текст по номеру (1-5) та країні"""
        field_name = f"cta_text_{number}_{'world' if country_code != 'UA' else 'ua'}"
        text = getattr(self, field_name, '')
        
        # Fallback до UA
        if not text and country_code != 'UA':
            text = getattr(self, f"cta_text_{number}_ua", '')
        
        return text
    
    def get_cta_url(self, number):
        """Отримати CTA URL для слайда по номеру (1-5)"""
        url = getattr(self, f'cta_url_{number}', '')
        return url if url else '#catalog'
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

