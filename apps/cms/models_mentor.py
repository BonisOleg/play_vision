"""
Моделі для сторінки "Ментор коучинг"
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class MentorHero(models.Model):
    """Hero блок - зображення"""
    image = models.ImageField('Зображення', upload_to='cms/mentor/hero/', max_length=500)
    
    is_active = models.BooleanField('Активно', default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_mentor_hero'
        verbose_name = 'Hero блок'
        verbose_name_plural = '💼 Ментор коучинг → Hero блок'
    
    def __str__(self):
        return "Hero - Ментор коучинг"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)


class MentorSection1Image(models.Model):
    """Секція 1 - 3 картинки з підписами"""
    position = models.PositiveIntegerField(
        'Позиція',
        validators=[MinValueValidator(1), MaxValueValidator(3)],
        help_text='Позиція картинки (1, 2 або 3)'
    )
    
    # Картинка UA
    image_ua = models.ImageField('Картинка (Україна)', upload_to='cms/mentor/section1/', max_length=500)
    caption_ua = models.CharField('Підпис (Україна)', max_length=200)
    
    # Картинка World
    image_world = models.ImageField('Картинка (Світ)', upload_to='cms/mentor/section1/', blank=True, max_length=500)
    caption_world = models.CharField('Підпис (Світ)', max_length=200, blank=True)
    
    is_active = models.BooleanField('Активно', default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_mentor_section1_images'
        verbose_name = 'Картинка'
        verbose_name_plural = '💼 Ментор коучинг → Секція 1 (3 картинки)'
        ordering = ['position']
    
    def __str__(self):
        return f"Картинка {self.position}"
    
    def get_image(self, country_code='UA'):
        if country_code == 'UA' or not self.image_world:
            return self.image_ua
        return self.image_world
    
    def get_caption(self, country_code='UA'):
        if country_code == 'UA' or not self.caption_world:
            return self.caption_ua
        return self.caption_world


class MentorSection2(models.Model):
    """Секція 2 - Заголовок + SVG"""
    # Заголовок UA/World
    title_ua = models.CharField('Заголовок (Україна)', max_length=200)
    title_world = models.CharField('Заголовок (Світ)', max_length=200, blank=True)
    
    # SVG 4 версії
    svg_ua_light = models.TextField('SVG UA (світла тема)')
    svg_ua_dark = models.TextField('SVG UA (темна тема)', blank=True)
    svg_world_light = models.TextField('SVG World (світла)', blank=True)
    svg_world_dark = models.TextField('SVG World (темна)', blank=True)
    
    is_active = models.BooleanField('Активно', default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_mentor_section2'
        verbose_name = 'Секція 2'
        verbose_name_plural = '💼 Ментор коучинг → Секція 2'
    
    def __str__(self):
        return "Секція 2 - Ментор"
    
    def get_title(self, country_code='UA'):
        return self.title_world if country_code != 'UA' and self.title_world else self.title_ua
    
    def get_svg(self, country_code='UA', theme='light'):
        field_name = f"svg_{'ua' if country_code == 'UA' else 'world'}_{theme}"
        svg = getattr(self, field_name, '')
        
        if not svg and country_code != 'UA':
            svg = getattr(self, f"svg_ua_{theme}", '')
        if not svg and theme == 'dark':
            svg = getattr(self, f"svg_{'ua' if country_code == 'UA' else 'world'}_light", '')
        
        return svg or self.svg_ua_light
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)


class MentorSection3(models.Model):
    """Секція 3 - SVG 4 версії"""
    # SVG 4 версії
    svg_ua_light = models.TextField('SVG UA (світла тема)')
    svg_ua_dark = models.TextField('SVG UA (темна тема)', blank=True)
    svg_world_light = models.TextField('SVG World (світла)', blank=True)
    svg_world_dark = models.TextField('SVG World (темна)', blank=True)
    
    is_active = models.BooleanField('Активно', default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_mentor_section3'
        verbose_name = 'Секція 3'
        verbose_name_plural = '💼 Ментор коучинг → Секція 3'
    
    def __str__(self):
        return "Секція 3 - Ментор"
    
    def get_svg(self, country_code='UA', theme='light'):
        field_name = f"svg_{'ua' if country_code == 'UA' else 'world'}_{theme}"
        svg = getattr(self, field_name, '')
        
        if not svg and country_code != 'UA':
            svg = getattr(self, f"svg_ua_{theme}", '')
        if not svg and theme == 'dark':
            svg = getattr(self, f"svg_{'ua' if country_code == 'UA' else 'world'}_light", '')
        
        return svg or self.svg_ua_light
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)


class MentorSection4(models.Model):
    """Секція 4 - Заголовок + Підзаголовок (показує команду)"""
    # Заголовок UA/World
    title_ua = models.CharField('Заголовок (Україна)', max_length=200)
    subtitle_ua = models.CharField('Підзаголовок (Україна)', max_length=300, blank=True)
    title_world = models.CharField('Заголовок (Світ)', max_length=200, blank=True)
    subtitle_world = models.CharField('Підзаголовок (Світ)', max_length=300, blank=True)
    
    is_active = models.BooleanField('Активно', default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_mentor_section4'
        verbose_name = 'Секція 4 + Команда'
        verbose_name_plural = '💼 Ментор коучинг → Секція 4'
    
    def __str__(self):
        return "Секція 4 - Ментор + Команда"
    
    def get_title(self, country_code='UA'):
        return self.title_world if country_code != 'UA' and self.title_world else self.title_ua
    
    def get_subtitle(self, country_code='UA'):
        return self.subtitle_world if country_code != 'UA' and self.subtitle_world else self.subtitle_ua
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)


class MentorCoachingSVG(models.Model):
    """SVG для секції Ментор коучинг на Головній сторінці"""
    # 4 версії
    svg_ua_light = models.TextField('SVG UA (світла тема)')
    svg_ua_dark = models.TextField('SVG UA (темна тема)', blank=True)
    svg_world_light = models.TextField('SVG World (світла)', blank=True)
    svg_world_dark = models.TextField('SVG World (темна)', blank=True)
    
    is_active = models.BooleanField('Активно', default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_mentor_coaching_svg'
        verbose_name = 'Ментор коучинг SVG'
        verbose_name_plural = '🏠 Головна → Ментор коучинг SVG'
    
    def __str__(self):
        return "Ментор коучинг SVG - Головна"
    
    def get_svg(self, country_code='UA', theme='light'):
        field_name = f"svg_{'ua' if country_code == 'UA' else 'world'}_{theme}"
        svg = getattr(self, field_name, '')
        
        if not svg and country_code != 'UA':
            svg = getattr(self, f"svg_ua_{theme}", '')
        if not svg and theme == 'dark':
            svg = getattr(self, f"svg_{'ua' if country_code == 'UA' else 'world'}_light", '')
        
        return svg or self.svg_ua_light
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

