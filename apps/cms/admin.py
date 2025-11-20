from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import (
    HeroSlide, FeaturedCourse, ExpertCard, EventGridCell, TrackingPixel, SiteSettings,
    # Про нас
    AboutHero, AboutSection2, AboutSection3, AboutSection4,
    # Хаб знань
    HubHero,
    # Ментор коучинг
    MentorHero, MentorSection1Image, MentorSection2, MentorSection3, MentorSection4,
    MentorCoachingSVG
)


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
                '<p class="admin-preview-caption">URL: {}</p>'
                '</div>',
                obj.image.url,
                obj.image.url
            )
        return "Зображення не завантажено"
    get_image_preview.short_description = 'Превью зображення'
    
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
                '<p class="admin-preview-caption">URL: {}</p>'
                '</div>',
                obj.photo.url,
                obj.photo.url
            )
        return "Фото не завантажено"
    get_photo_large.short_description = 'Превью фото'
    
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


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Admin for global site settings (Singleton)"""
    fieldsets = (
        ('Зовнішні посилання', {
            'fields': ('external_auth_url', 'external_join_url_default'),
            'description': mark_safe("""
                <div class="cms-help-box">
                    <h4>🔗 Налаштування зовнішніх URL</h4>
                    <ul>
                        <li><strong>URL зовнішньої авторизації:</strong> Посилання на Квігу або інший сайт для входу/реєстрації</li>
                        <li><strong>URL "Приєднатись" за замовчуванням:</strong> Використовується на сторінках курсів, якщо не вказано окремо</li>
                    </ul>
                </div>
            """)
        }),
        ('Метадані', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('updated_at',)
    
    def has_add_permission(self, request):
        # Singleton - дозволити створення тільки якщо немає запису
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Заборонити видалення
        return False
    
    class Media:
        css = {'all': ('admin/css/playvision-admin.css',)}
        js = ('admin/js/playvision-admin.js',)
