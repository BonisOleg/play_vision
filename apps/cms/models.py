from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Page(models.Model):
    """
    Статичні сторінки (About, Contacts, Legal тощо)
    """
    STATUS_CHOICES = [
        ('draft', 'Чернетка'),
        ('published', 'Опубліковано'),
        ('archived', 'Архівовано'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    excerpt = models.TextField(blank=True, help_text='Короткий опис для превью')
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=300, blank=True)
    
    # Статус та публікація
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    
    # Автор та час
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='cms_pages')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'cms_pages'
        verbose_name = 'CMS Page'
        verbose_name_plural = 'CMS Pages'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Banner(models.Model):
    """
    Банери для різних розділів сайту
    """
    BANNER_TYPES = [
        ('hero', 'Hero банер'),
        ('promotion', 'Промо'),
        ('announcement', 'Оголошення'),
        ('subscription', 'Підписка'),
        ('event', 'Івент'),
    ]
    
    POSITIONS = [
        ('header', 'Хедер'),
        ('hero', 'Hero секція'),
        ('sidebar', 'Бокова панель'),
        ('footer', 'Футер'),
        ('popup', 'Спливаюче вікно'),
    ]
    
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    banner_type = models.CharField(max_length=20, choices=BANNER_TYPES)
    position = models.CharField(max_length=20, choices=POSITIONS)
    
    # Контент
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='cms/banners/', blank=True)
    background_color = models.CharField(max_length=7, default='#ffffff')
    text_color = models.CharField(max_length=7, default='#000000')
    
    # CTA
    cta_text = models.CharField(max_length=50, blank=True)
    cta_url = models.CharField(max_length=200, blank=True)
    cta_button_color = models.CharField(max_length=7, default='#ff6b35')
    
    # Відображення
    is_active = models.BooleanField(default=True)
    show_from = models.DateTimeField(null=True, blank=True)
    show_until = models.DateTimeField(null=True, blank=True)
    priority = models.PositiveIntegerField(default=0, help_text='Більше число = вища пріоритетність')
    
    # Цільова аудиторія
    show_to_guests = models.BooleanField(default=True)
    show_to_users = models.BooleanField(default=True)
    show_to_subscribers = models.BooleanField(default=True)
    
    # Статистика
    view_count = models.PositiveIntegerField(default=0)
    click_count = models.PositiveIntegerField(default=0)
    
    # Метадані
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_banners'
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.position})"


class MenuItem(models.Model):
    """
    Елементи меню навігації
    """
    MENU_TYPES = [
        ('main', 'Головне меню'),
        ('footer', 'Меню футера'),
        ('mobile', 'Мобільне меню'),
        ('user', 'Меню користувача'),
    ]
    
    menu_type = models.CharField(max_length=20, choices=MENU_TYPES)
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=200, help_text='Відносний або абсолютний URL')
    icon = models.CharField(max_length=50, blank=True, help_text='CSS клас іконки')
    
    # Ієрархія
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                             related_name='children')
    order = models.PositiveIntegerField(default=0)
    
    # Відображення
    is_active = models.BooleanField(default=True)
    open_in_new_tab = models.BooleanField(default=False)
    
    # Права доступу
    require_auth = models.BooleanField(default=False)
    require_subscription = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'cms_menu_items'
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'
        ordering = ['menu_type', 'order']
    
    def __str__(self):
        return f"{self.menu_type}: {self.title}"


class FAQ(models.Model):
    """
    Часті питання
    """
    CATEGORIES = [
        ('general', 'Загальні'),
        ('subscription', 'Підписка'),
        ('courses', 'Курси'),
        ('events', 'Івенти'),
        ('payments', 'Оплата'),
        ('technical', 'Технічні'),
    ]
    
    question = models.CharField(max_length=300)
    answer = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORIES)
    
    # Відображення
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    # Статистика
    view_count = models.PositiveIntegerField(default=0)
    helpful_votes = models.PositiveIntegerField(default=0)
    not_helpful_votes = models.PositiveIntegerField(default=0)
    
    # Метадані
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_faq'
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['category', 'order']
    
    def __str__(self):
        return self.question[:100]


class Testimonial(models.Model):
    """
    Відгуки та рекомендації
    """
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    rating = models.PositiveIntegerField(default=5, help_text='Рейтинг від 1 до 5')
    
    # Медіа
    photo = models.ImageField(upload_to='cms/testimonials/', blank=True)
    
    # Відображення
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    show_on_homepage = models.BooleanField(default=False)
    
    # Метадані
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_testimonials'
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.rating}★"


class Setting(models.Model):
    """
    Глобальні налаштування сайту
    """
    SETTING_TYPES = [
        ('string', 'Рядок'),
        ('text', 'Текст'),
        ('boolean', 'Булевий'),
        ('integer', 'Число'),
        ('float', 'Десяткове'),
        ('json', 'JSON'),
    ]
    
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    setting_type = models.CharField(max_length=20, choices=SETTING_TYPES, default='string')
    description = models.TextField(help_text='Опис призначення налаштування')
    
    # Групування
    group = models.CharField(max_length=50, default='general', 
                           help_text='Група налаштувань (general, email, payment тощо)')
    
    # Відображення в адмінці
    is_public = models.BooleanField(default=False, help_text='Доступно через API')
    order = models.PositiveIntegerField(default=0)
    
    # Метадані
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_settings'
        verbose_name = 'Setting'
        verbose_name_plural = 'Settings'
        ordering = ['group', 'order']
    
    def __str__(self):
        return f"{self.group}.{self.key}"
    
    def get_value(self):
        """Отримати значення з правильним типом"""
        if self.setting_type == 'boolean':
            return self.value.lower() in ['true', '1', 'yes']
        elif self.setting_type == 'integer':
            return int(self.value)
        elif self.setting_type == 'float':
            return float(self.value)
        elif self.setting_type == 'json':
            import json
            return json.loads(self.value)
        return self.value


class ContentBlock(models.Model):
    """
    Блоки контенту для збирання сторінок
    """
    BLOCK_TYPES = [
        ('text', 'Текстовий блок'),
        ('image', 'Зображення'),
        ('video', 'Відео'),
        ('carousel', 'Карусель'),
        ('cta', 'Заклик до дії'),
        ('testimonials', 'Відгуки'),
        ('faq', 'FAQ'),
        ('stats', 'Статистика'),
    ]
    
    name = models.CharField(max_length=100)
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPES)
    content = models.JSONField(help_text='Контент блоку у форматі JSON')
    
    # Стилізація
    css_classes = models.CharField(max_length=200, blank=True)
    custom_css = models.TextField(blank=True)
    
    # Відображення
    is_active = models.BooleanField(default=True)
    
    # Метадані
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_content_blocks'
        verbose_name = 'Content Block'
        verbose_name_plural = 'Content Blocks'
    
    def __str__(self):
        return f"{self.name} ({self.block_type})"


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
                             help_text='Recommended: 1920×1080 px')
    video = models.FileField('Video', upload_to='cms/hero/videos/', blank=True,
                            help_text='MP4 format')
    
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
        verbose_name_plural = 'Hero Слайди'
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
        """Auto-optimize images"""
        if self.image and hasattr(self.image, 'file'):
            try:
                from PIL import Image
                from io import BytesIO
                from django.core.files.uploadedfile import InMemoryUploadedFile
                
                img = Image.open(self.image)
                
                if img.height > 1080 or img.width > 1920:
                    # Convert RGBA to RGB
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    
                    # Resize
                    img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
                    
                    # Save
                    output = BytesIO()
                    img.save(output, format='JPEG', optimize=True, quality=85)
                    output.seek(0)
                    
                    self.image = InMemoryUploadedFile(
                        output, 'ImageField',
                        f"{self.image.name.split('.')[0]}.jpg",
                        'image/jpeg', output.getbuffer().nbytes, None
                    )
            except Exception:
                pass
        
        super().save(*args, **kwargs)


class PageSection(models.Model):
    """Page sections"""
    SECTION_TYPES = [
        ('hero', 'Hero'),
        ('featured_courses', 'Featured Курси'),
        ('courses', 'Курси'),
        ('mentor', 'Ментор коучинг'),
        ('experts', 'Експерти'),
        ('cta', 'Call to Action'),
        ('custom', 'Кастомна секція'),
    ]
    
    page = models.CharField('Сторінка', max_length=50, default='home')
    section_type = models.CharField('Тип секції', max_length=30, choices=SECTION_TYPES)
    title = models.CharField('Заголовок', max_length=200, blank=True)
    subtitle = models.CharField('Підзаголовок', max_length=300, blank=True)
    
    # Background
    bg_image = models.ImageField('Фонове зображення', upload_to='cms/sections/', blank=True)
    bg_color = models.CharField('Колір фону', max_length=7, default='#ffffff')
    
    # Display
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активна', default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_page_sections'
        verbose_name = 'Секція сторінки'
        verbose_name_plural = 'Секції сторінок'
        ordering = ['page', 'order']
    
    def __str__(self):
        return f"{self.page}: {self.get_section_type_display()}"


class SectionBlock(models.Model):
    """Blocks within page sections"""
    BLOCK_TYPES = [
        ('text', 'Текст'),
        ('image', 'Зображення'),
        ('card', 'Картка'),
        ('course_card', 'Картка курсу'),
    ]
    
    section = models.ForeignKey(PageSection, on_delete=models.CASCADE, related_name='blocks')
    block_type = models.CharField('Тип блоку', max_length=20, choices=BLOCK_TYPES)
    
    title = models.CharField('Заголовок', max_length=200, blank=True)
    text = models.TextField('Текст', blank=True)
    image = models.ImageField('Зображення', upload_to='cms/blocks/', blank=True)
    
    # CTA
    cta_text = models.CharField('Текст кнопки', max_length=50, blank=True)
    cta_url = models.CharField('URL кнопки', max_length=200, blank=True)
    
    # Display
    order = models.PositiveIntegerField('Порядок', default=0)
    
    class Meta:
        db_table = 'cms_section_blocks'
        verbose_name = 'Блок секції'
        verbose_name_plural = 'Блоки секцій'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.section.section_type}: {self.title or self.block_type}"


class ExpertCard(models.Model):
    """Expert cards"""
    name = models.CharField('Ім\'я', max_length=100)
    position = models.CharField('Посада', max_length=150)
    specialization = models.CharField('Спеціалізація', max_length=200, blank=True)
    bio = models.TextField('Біографія', blank=True)
    
    photo = models.ImageField('Фото', upload_to='cms/experts/', blank=True,
                             help_text='Рекомендований розмір: 400×400 px')
    
    # Display
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активний', default=True)
    show_on_homepage = models.BooleanField('Показувати на головній', default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_expert_cards'
        verbose_name = 'Експерт'
        verbose_name_plural = 'Експерти'
        ordering = ['order']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-optimize images"""
        if self.photo and hasattr(self.photo, 'file'):
            try:
                from PIL import Image
                from io import BytesIO
                from django.core.files.uploadedfile import InMemoryUploadedFile
                
                img = Image.open(self.photo)
                
                if img.height > 400 or img.width > 400:
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    
                    img.thumbnail((400, 400), Image.Resampling.LANCZOS)
                    
                    output = BytesIO()
                    img.save(output, format='JPEG', optimize=True, quality=85)
                    output.seek(0)
                    
                    self.photo = InMemoryUploadedFile(
                        output, 'ImageField',
                        f"{self.photo.name.split('.')[0]}.jpg",
                        'image/jpeg', output.getbuffer().nbytes, None
                    )
            except Exception:
                pass
        
        super().save(*args, **kwargs)


class HexagonItem(models.Model):
    """Hexagon items for mentor-coaching section"""
    title = models.CharField('Назва', max_length=100)
    icon_svg = models.TextField('SVG іконка', help_text='Вставте SVG код іконки')
    description = models.TextField('Опис', blank=True)
    color = models.CharField('Колір', max_length=7, default='#ff6b35')
    
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активний', default=True)
    
    class Meta:
        db_table = 'cms_hexagon_items'
        verbose_name = 'Hexagon елемент'
        verbose_name_plural = 'Hexagon елементи'
        ordering = ['order']
    
    def __str__(self):
        return self.title


class FeaturedCourse(models.Model):
    """
    Featured courses for homepage carousel (7-12 courses)
    """
    course = models.ForeignKey(
        'content.Course',
        on_delete=models.CASCADE,
        verbose_name='Курс',
        help_text='Курс для відображення на головній'
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
        verbose_name = 'Вибраний курс'
        verbose_name_plural = 'Вибрані курси'
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


class PageSVG(models.Model):
    """
    SVG icons with 4 versions: UA light/dark + World light/dark
    """
    name = models.CharField(
        'Назва',
        max_length=100,
        unique=True,
        help_text='Унікальна назва SVG (наприклад: about_section2)'
    )
    page = models.CharField(
        'Сторінка',
        max_length=50,
        db_index=True,
        help_text='Сторінка де використовується (about, mentor, home)'
    )
    section = models.CharField(
        'Секція',
        max_length=50,
        blank=True,
        help_text='Номер секції (section2, section3 тощо)'
    )
    
    # 4 versions of SVG code
    svg_ua_light = models.TextField(
        'SVG (Ukraine, Light)',
        help_text='SVG код для України в світлій темі'
    )
    svg_ua_dark = models.TextField(
        'SVG (Ukraine, Dark)',
        blank=True,
        help_text='SVG код для України в темній темі'
    )
    svg_world_light = models.TextField(
        'SVG (World, Light)',
        blank=True,
        help_text='SVG код для світу в світлій темі (якщо порожнє - показується UA)'
    )
    svg_world_dark = models.TextField(
        'SVG (World, Dark)',
        blank=True,
        help_text='SVG код для світу в темній темі'
    )
    
    is_active = models.BooleanField('Активний', default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cms_page_svg'
        verbose_name = 'SVG елемент'
        verbose_name_plural = 'SVG елементи'
        ordering = ['page', 'section', 'name']
        indexes = [
            models.Index(fields=['page', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.page}/{self.section}: {self.name}"
    
    def get_svg(self, country='UA', theme='light'):
        """
        Get appropriate SVG code based on country and theme
        
        Args:
            country: 'UA' or 'WORLD'
            theme: 'light' or 'dark'
        
        Returns:
            str: SVG code
        """
        field_name = f"svg_{country.lower()}_{theme}"
        svg_code = getattr(self, field_name, '')
        
        # Fallback to UA if World version is empty
        if not svg_code and country != 'UA':
            field_name = f"svg_ua_{theme}"
            svg_code = getattr(self, field_name, '')
        
        # Fallback to light if dark version is empty
        if not svg_code and theme == 'dark':
            field_name = f"svg_{country.lower()}_light"
            svg_code = getattr(self, field_name, '')
        
        return svg_code


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
        verbose_name = 'Комірка сітки івентів'
        verbose_name_plural = 'Комірки сітки івентів'
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
        verbose_name_plural = 'Tracking Pixels'
        ordering = ['-created_at']
        unique_together = [('pixel_type', 'pixel_id')]
    
    def __str__(self):
        return f"{self.name} ({self.get_pixel_type_display()})"


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
    # Існуючі
    'Page', 'Banner', 'MenuItem', 'FAQ', 'Testimonial', 'Setting', 'ContentBlock',
    'HeroSlide', 'PageSection', 'SectionBlock', 'ExpertCard', 'HexagonItem',
    'FeaturedCourse', 'PageSVG', 'EventGridCell', 'TrackingPixel',
    # Про нас
    'AboutHero', 'AboutSection2', 'AboutSection3', 'AboutSection4',
    # Хаб знань
    'HubHero',
    # Ментор коучинг
    'MentorHero', 'MentorSection1Image', 'MentorSection2', 'MentorSection3', 'MentorSection4',
    # Ментор на головній
    'MentorCoachingSVG',
]