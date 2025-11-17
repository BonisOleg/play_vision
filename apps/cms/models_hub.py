"""
Моделі для сторінки "Хаб знань"
"""
from django.db import models


class HubHero(models.Model):
    """Hero секція для Хаб знань - фон + 3 заголовки"""
    # Фонове зображення
    background_image = models.ImageField('Фонове зображення', upload_to='cms/hub/hero/')
    
    # Заголовок 1 (UA/World)
    title_1_ua = models.CharField('Заголовок 1 (Україна)', max_length=200)
    subtitle_1_ua = models.CharField('Підзаголовок 1 (Україна)', max_length=300, blank=True)
    title_1_world = models.CharField('Заголовок 1 (Світ)', max_length=200, blank=True)
    subtitle_1_world = models.CharField('Підзаголовок 1 (Світ)', max_length=300, blank=True)
    
    # Заголовок 2 (UA/World)
    title_2_ua = models.CharField('Заголовок 2 (Україна)', max_length=200, blank=True)
    subtitle_2_ua = models.CharField('Підзаголовок 2 (Україна)', max_length=300, blank=True)
    title_2_world = models.CharField('Заголовок 2 (Світ)', max_length=200, blank=True)
    subtitle_2_world = models.CharField('Підзаголовок 2 (Світ)', max_length=300, blank=True)
    
    # Заголовок 3 (UA/World)
    title_3_ua = models.CharField('Заголовок 3 (Україна)', max_length=200, blank=True)
    subtitle_3_ua = models.CharField('Підзаголовок 3 (Україна)', max_length=300, blank=True)
    title_3_world = models.CharField('Заголовок 3 (Світ)', max_length=200, blank=True)
    subtitle_3_world = models.CharField('Підзаголовок 3 (Світ)', max_length=300, blank=True)
    
    is_active = models.BooleanField('Активно', default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_hub_hero'
        verbose_name = 'Hero секція'
        verbose_name_plural = '🎓 Хаб знань → Hero секція'
    
    def __str__(self):
        return "Hero - Хаб знань"
    
    def get_title(self, number, country_code='UA'):
        """Отримати заголовок по номеру (1-3) та країні"""
        field_name = f"title_{number}_{'world' if country_code != 'UA' else 'ua'}"
        title = getattr(self, field_name, '')
        
        # Fallback до UA
        if not title and country_code != 'UA':
            title = getattr(self, f"title_{number}_ua", '')
        
        return title
    
    def get_subtitle(self, number, country_code='UA'):
        """Отримати підзаголовок по номеру (1-3) та країні"""
        field_name = f"subtitle_{number}_{'world' if country_code != 'UA' else 'ua'}"
        subtitle = getattr(self, field_name, '')
        
        # Fallback до UA
        if not subtitle and country_code != 'UA':
            subtitle = getattr(self, f"subtitle_{number}_ua", '')
        
        return subtitle
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

