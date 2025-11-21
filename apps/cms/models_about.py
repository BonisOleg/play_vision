"""
Моделі для сторінки "Про нас"
"""
from django.db import models


class AboutHero(models.Model):
    """Hero секція для сторінки Про нас"""
    # Ukraine version
    title_ua = models.CharField('Заголовок (Україна)', max_length=200)
    subtitle_ua = models.CharField('Підзаголовок (Україна)', max_length=300, blank=True)
    image_ua = models.ImageField('Зображення (Україна)', upload_to='cms/about/hero/', blank=True, max_length=500)
    
    # World version
    title_world = models.CharField('Заголовок (Світ)', max_length=200, blank=True,
                                   help_text='Залиште порожнім щоб показувати українську версію')
    subtitle_world = models.CharField('Підзаголовок (Світ)', max_length=300, blank=True)
    image_world = models.ImageField('Зображення (Світ)', upload_to='cms/about/hero/', blank=True, max_length=500)
    
    is_active = models.BooleanField('Активно', default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_about_hero'
        verbose_name = 'Hero секція'
        verbose_name_plural = '📖 Про нас → Hero секція'
    
    def __str__(self):
        return f"Hero - Про нас"
    
    def get_title(self, country_code='UA'):
        if country_code == 'UA' or not self.title_world:
            return self.title_ua
        return self.title_world
    
    def get_subtitle(self, country_code='UA'):
        if country_code == 'UA' or not self.subtitle_world:
            return self.subtitle_ua
        return self.subtitle_world
    
    def get_image(self, country_code='UA'):
        if country_code == 'UA' or not self.image_world:
            return self.image_ua
        return self.image_world
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)


class AboutSection2(models.Model):
    """Секція 2 - PNG/SVG 4 версії (текстові поля)
    
    Поля приймають:
    - SVG код безпосередньо (<svg>...</svg>)
    - PNG в форматі base64 data URI (data:image/png;base64,...)
    - URL зображення (для зворотної сумісності)
    """
    # 4 текстові поля для PNG/SVG
    image_ua_light = models.TextField('PNG/SVG UA (світла тема)')
    image_ua_dark = models.TextField('PNG/SVG UA (темна тема)', blank=True)
    image_world_light = models.TextField('PNG/SVG World (світла)', blank=True)
    image_world_dark = models.TextField('PNG/SVG World (темна)', blank=True)
    
    is_active = models.BooleanField('Активно', default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_about_section2'
        verbose_name = 'Секція 2'
        verbose_name_plural = '📖 Про нас → Секція 2'
    
    def __str__(self):
        return "Секція 2 - Про нас"
    
    def get_image(self, country_code='UA', theme='light'):
        field_name = f"image_{'ua' if country_code == 'UA' else 'world'}_{theme}"
        image = getattr(self, field_name, None)
        
        # Fallback: World → UA, Dark → Light
        if not image and country_code != 'UA':
            field_name = f"image_ua_{theme}"
            image = getattr(self, field_name, None)
        
        if not image and theme == 'dark':
            field_name = f"image_{'ua' if country_code == 'UA' else 'world'}_light"
            image = getattr(self, field_name, None)
        
        return image or self.image_ua_light
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)


class AboutSection3(models.Model):
    """Секція 3 - Заголовок + SVG"""
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
        db_table = 'cms_about_section3'
        verbose_name = 'Секція 3'
        verbose_name_plural = '📖 Про нас → Секція 3'
    
    def __str__(self):
        return "Секція 3 - Про нас"
    
    def get_title(self, country_code='UA'):
        return self.title_world if country_code != 'UA' and self.title_world else self.title_ua
    
    def get_svg(self, country_code='UA', theme='light'):
        field_name = f"svg_{'ua' if country_code == 'UA' else 'world'}_{theme}"
        svg = getattr(self, field_name, '')
        
        # Fallback
        if not svg and country_code != 'UA':
            svg = getattr(self, f"svg_ua_{theme}", '')
        if not svg and theme == 'dark':
            svg = getattr(self, f"svg_{'ua' if country_code == 'UA' else 'world'}_light", '')
        
        return svg or self.svg_ua_light
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)


class AboutSection4(models.Model):
    """Секція 4 - Заголовок + SVG"""
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
        db_table = 'cms_about_section4'
        verbose_name = 'Секція 4'
        verbose_name_plural = '📖 Про нас → Секція 4'
    
    def __str__(self):
        return "Секція 4 - Про нас"
    
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

