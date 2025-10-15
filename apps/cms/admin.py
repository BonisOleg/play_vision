from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import (
    Page, Banner, MenuItem, FAQ, Testimonial, Setting, ContentBlock,
    HeroSlide, PageSection, SectionBlock, ExpertCard, HexagonItem
)


# Inline для блоків секцій
class SectionBlockInline(admin.TabularInline):
    model = SectionBlock
    extra = 1
    fields = ['block_type', 'title', 'text', 'image', 'cta_text', 'cta_url', 'order']
    classes = ['collapse']


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ['get_preview', 'title', 'badge', 'order', 'is_active', 'created_at']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'subtitle', 'badge']
    readonly_fields = ['get_image_preview', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('title', 'subtitle', 'badge')
        }),
        ('Медіа', {
            'fields': ('image', 'get_image_preview', 'video'),
            'description': mark_safe("""
                <div class="cms-help-box">
                    <h4>📐 Рекомендовані розміри:</h4>
                    <ul>
                        <li><strong>Зображення:</strong> 1920×1080 px (16:9)</li>
                        <li><strong>Відео:</strong> MP4, макс 50MB</li>
                    </ul>
                </div>
            """)
        }),
        ('Кнопка (Call to Action)', {
            'fields': ('cta_text', 'cta_url'),
        }),
        ('Відображення', {
            'fields': ('order', 'is_active'),
        }),
        ('Метадані', {
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
