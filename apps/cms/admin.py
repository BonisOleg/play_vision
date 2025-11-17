from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import (
    Page, Banner, MenuItem, FAQ, Testimonial, Setting, ContentBlock,
    HeroSlide, PageSection, SectionBlock, ExpertCard, HexagonItem,
    FeaturedCourse, PageSVG, EventGridCell, TrackingPixel,
    # Про нас
    AboutHero, AboutSection2, AboutSection3, AboutSection4,
    # Хаб знань
    HubHero,
    # Ментор коучинг
    MentorHero, MentorSection1Image, MentorSection2, MentorSection3, MentorSection4,
    MentorCoachingSVG
)


# Inline для блоків секцій
class SectionBlockInline(admin.TabularInline):
    model = SectionBlock
    extra = 1
    fields = ['block_type', 'title', 'text', 'image', 'cta_text', 'cta_url', 'order']
    classes = ['collapse']


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ['get_preview', 'title_ua', 'badge', 'order', 'is_active', 'created_at']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title_ua', 'title_world', 'subtitle_ua', 'badge']
    readonly_fields = ['get_image_preview', 'created_at', 'updated_at']
    
    fieldsets = (
        ('🇺🇦 Ukraine Version (Primary)', {
            'fields': ('title_ua', 'subtitle_ua', 'cta_text_ua'),
            'description': 'Main content shown in Ukraine'
        }),
        ('🌍 World Version (Fallback)', {
            'fields': ('title_world', 'subtitle_world', 'cta_text_world'),
            'description': 'Alternative content for other countries (leave blank to use Ukraine version)',
            'classes': ('collapse',)
        }),
        ('Media & CTA', {
            'fields': ('image', 'get_image_preview', 'video', 'badge', 'cta_url'),
            'description': mark_safe("""
                <div class="cms-help-box">
                    <h4>📐 Recommended sizes:</h4>
                    <ul>
                        <li><strong>Image:</strong> 1920×1080 px (16:9)</li>
                        <li><strong>Video:</strong> MP4, max 50MB</li>
                    </ul>
                </div>
            """)
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active'),
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
    
    def get_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" class="admin-list-thumbnail" />',
                obj.image.url
            )
        return format_html('<div class="admin-placeholder">📷</div>')
    get_preview.short_description = 'Превью'
    
    def get_image_preview(self, obj):
        if obj.image:
            return format_html(
                '<div class="admin-preview-large">'
                '<img src="{}" class="admin-preview-image" />'
                '<p class="admin-preview-caption">Розмір: {} | {}</p>'
                '</div>',
                obj.image.url,
                f"{obj.image.width}×{obj.image.height}" if hasattr(obj.image, 'width') else 'N/A',
                f"{obj.image.size / 1024:.1f} KB" if hasattr(obj.image, 'size') else ''
            )
        return "Зображення не завантажено"
    get_image_preview.short_description = 'Превью зображення'
    
    class Media:
        css = {'all': ('admin/css/cms_admin.css',)}
        js = ('admin/js/cms_admin.js',)


@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'page', 'section_type', 'title', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['page', 'section_type', 'is_active']
    search_fields = ['title', 'subtitle']
    inlines = [SectionBlockInline]
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('page', 'section_type', 'title', 'subtitle')
        }),
        ('Фон', {
            'fields': ('bg_image', 'bg_color'),
        }),
        ('Відображення', {
            'fields': ('order', 'is_active'),
        }),
    )
    
    class Media:
        css = {'all': ('admin/css/cms_admin.css',)}
        js = ('admin/js/cms_admin.js',)


@admin.register(ExpertCard)
class ExpertCardAdmin(admin.ModelAdmin):
    list_display = ['get_photo_preview', 'name', 'position', 'order', 'is_active', 'show_on_homepage']
    list_editable = ['order', 'is_active', 'show_on_homepage']
    list_filter = ['is_active', 'show_on_homepage']
    search_fields = ['name', 'position', 'specialization']
    readonly_fields = ['get_photo_large', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'position', 'specialization', 'bio')
        }),
        ('Фото', {
            'fields': ('photo', 'get_photo_large'),
            'description': '<p><strong>Розмір:</strong> 400×400 px (квадрат)</p>'
        }),
        ('Відображення', {
            'fields': ('order', 'is_active', 'show_on_homepage'),
        }),
        ('Метадані', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
    
    def get_photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" class="admin-list-thumbnail admin-list-thumbnail-round" />',
                obj.photo.url
            )
        return format_html('<div class="admin-placeholder">👤</div>')
    get_photo_preview.short_description = 'Фото'
    
    def get_photo_large(self, obj):
        if obj.photo:
            return format_html(
                '<div class="admin-preview-large">'
                '<img src="{}" class="admin-preview-expert" />'
                '</div>',
                obj.photo.url
            )
        return "Фото не завантажено"
    get_photo_large.short_description = 'Превью фото'
    
    class Media:
        css = {'all': ('admin/css/cms_admin.css',)}
        js = ('admin/js/cms_admin.js',)


@admin.register(HexagonItem)
class HexagonItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'color', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'description']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('title', 'description')
        }),
        ('SVG іконка', {
            'fields': ('icon_svg',),
            'description': mark_safe("""
                <div class="cms-help-box">
                    <p>Вставте SVG код іконки. Приклад:</p>
                    <code>&lt;path d="M12 2C6.48 2 2 6.48..."&gt;&lt;/path&gt;</code>
                </div>
            """)
        }),
        ('Стилізація', {
            'fields': ('color',),
            'description': '<p>HEX колір (наприклад: #ff6b35)</p>'
        }),
        ('Відображення', {
            'fields': ('order', 'is_active'),
        }),
    )
    
    class Media:
        css = {'all': ('admin/css/cms_admin.css',)}
        js = ('admin/js/cms_admin.js',)


@admin.register(FeaturedCourse)
class FeaturedCourseAdmin(admin.ModelAdmin):
    """Admin for featured courses carousel (7-12 courses)"""
    list_display = ['course', 'page', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['page', 'is_active']
    search_fields = ['course__title']
    raw_id_fields = ('course',)
    ordering = ['page', 'order']
    
    fieldsets = (
        ('Course Selection', {
            'fields': ('course', 'page', 'order'),
            'description': 'Select course to feature. Order determines carousel position (1-12).'
        }),
        ('Display', {
            'fields': ('is_active',),
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('course')
    
    class Media:
        css = {'all': ('admin/css/playvision-admin.css',)}
        js = ('admin/js/playvision-admin.js',)


@admin.register(PageSVG)
class PageSVGAdmin(admin.ModelAdmin):
    """Admin for SVG icons with 4 versions"""
    list_display = ['name', 'page', 'section', 'is_active']
    list_filter = ['page', 'is_active']
    search_fields = ['name', 'page', 'section']
    ordering = ['page', 'section', 'name']
    
    fieldsets = (
        ('Location', {
            'fields': ('name', 'page', 'section'),
            'description': 'Where this SVG is used (e.g. page=about, section=section2)'
        }),
        ('Ukraine Version', {
            'fields': ('svg_ua_light', 'svg_ua_dark'),
            'description': 'SVG code for Ukraine audience (light and dark themes)'
        }),
        ('World Version (Optional)', {
            'fields': ('svg_world_light', 'svg_world_dark'),
            'description': 'SVG code for non-Ukraine audience (leave blank to use Ukraine version)',
            'classes': ('collapse',)
        }),
        ('Display', {
            'fields': ('is_active',),
        }),
    )
    
    class Media:
        css = {'all': ('admin/css/playvision-admin.css',)}
        js = ('admin/js/playvision-admin.js',)


@admin.register(EventGridCell)
class EventGridCellAdmin(admin.ModelAdmin):
    """Admin for events hero grid (9 cells)"""
    list_display = ['position', 'get_image_preview', 'alt_text', 'is_active']
    list_editable = ['is_active']
    list_filter = ['is_active']
    ordering = ['position']
    
    fieldsets = (
        ('Position', {
            'fields': ('position',),
            'description': 'Grid position: 1=top-left, 9=bottom-right'
        }),
        ('Image/GIF', {
            'fields': ('image', 'alt_text'),
            'description': 'Upload image or GIF animation'
        }),
        ('Display', {
            'fields': ('is_active',),
        }),
    )
    
    readonly_fields = ['get_image_preview']
    
    def get_image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" class="pv-grid-preview" style="max-width: 150px; border-radius: 6px;" />',
                obj.image.url
            )
        return "No image"
    get_image_preview.short_description = 'Preview'
    
    class Media:
        css = {'all': ('admin/css/playvision-admin.css',)}
        js = ('admin/js/playvision-admin.js',)


@admin.register(TrackingPixel)
class TrackingPixelAdmin(admin.ModelAdmin):
    """Admin for Facebook & Google tracking pixels"""
    list_display = ['name', 'pixel_type', 'pixel_id', 'placement', 'is_active']
    list_editable = ['is_active']
    list_filter = ['pixel_type', 'placement', 'is_active']
    search_fields = ['name', 'pixel_id']
    
    fieldsets = (
        ('Pixel Information', {
            'fields': ('name', 'pixel_type', 'pixel_id'),
            'description': 'Basic pixel identification'
        }),
        ('Code Snippet', {
            'fields': ('code_snippet',),
            'description': mark_safe("""
                <div class="cms-help-box">
                    <p>Paste complete pixel code including &lt;script&gt; tags.</p>
                    <p>Example: Facebook Pixel, Google Analytics gtag.js code</p>
                </div>
            """)
        }),
        ('Placement', {
            'fields': ('placement',),
            'description': 'Where to inject the pixel code in templates'
        }),
        ('Status', {
            'fields': ('is_active',),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    class Media:
        css = {'all': ('admin/css/playvision-admin.css',)}
        js = ('admin/js/playvision-admin.js',)


# Реєстрація існуючих моделей (якщо ще не зареєстровані)
@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'status', 'is_featured', 'created_at']
    list_filter = ['status', 'is_featured']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'banner_type', 'position', 'is_active', 'priority']
    list_filter = ['banner_type', 'position', 'is_active']
    list_editable = ['is_active', 'priority']
    search_fields = ['title', 'content']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'menu_type', 'url', 'order', 'is_active']
    list_filter = ['menu_type', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'url']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'is_featured', 'is_active', 'order']
    list_filter = ['category', 'is_featured', 'is_active']
    list_editable = ['is_featured', 'is_active', 'order']
    search_fields = ['question', 'answer']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'is_featured', 'show_on_homepage', 'is_active']
    list_filter = ['rating', 'is_featured', 'show_on_homepage', 'is_active']
    list_editable = ['is_featured', 'show_on_homepage', 'is_active']
    search_fields = ['name', 'content']


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'group', 'setting_type', 'is_public', 'order']
    list_filter = ['group', 'setting_type', 'is_public']
    list_editable = ['order']
    search_fields = ['key', 'value', 'description']


@admin.register(ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    list_display = ['name', 'block_type', 'is_active']
    list_filter = ['block_type', 'is_active']
    search_fields = ['name']
