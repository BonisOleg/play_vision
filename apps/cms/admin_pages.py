"""
Admin для сторінок сайту (Про нас, Хаб, Ментор)
"""
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import (
    AboutHero, AboutSection2, AboutSection3, AboutSection4,
    HubHero,
    MentorHero, MentorSection1Image, MentorSection2, MentorSection3, MentorSection4,
    MentorCoachingSVG
)


# ============================================
# 📖 ПРО НАС
# ============================================

@admin.register(AboutHero)
class AboutHeroAdmin(admin.ModelAdmin):
    """Hero секція - Про нас"""
    
    fieldsets = (
        ('🇺🇦 Українська версія - Зображення', {
            'fields': ('title_ua', 'subtitle_ua', 'image_ua')
        }),
        ('🇺🇦 Українська версія - Відео', {
            'fields': ('video_library_id_ua', 'video_id_ua'),
            'description': mark_safe("""
                <div class="cms-help-box">
                    <h4>📹 BunnyNet відео інтеграція</h4>
                    <p><strong>Де взяти ID?</strong></p>
                    <ul>
                        <li><strong>Library ID:</strong> Панель BunnyNet → Stream → Ваша бібліотека → ID зверху</li>
                        <li><strong>Video ID:</strong> Відкрийте відео → URL містить GUID (напр. abc123-def456-...)</li>
                    </ul>
                    <p><strong>Якість:</strong> Desktop = найвища, Mobile = 720p (автоматично)</p>
                </div>
            """)
        }),
        ('🌍 Світова версія - Зображення', {
            'fields': ('title_world', 'subtitle_world', 'image_world'),
            'classes': ('collapse',)
        }),
        ('🌍 Світова версія - Відео', {
            'fields': ('video_library_id_world', 'video_id_world'),
            'classes': ('collapse',)
        }),
        ('Налаштування', {
            'fields': ('video_enabled', 'is_active')
        }),
    )
    
    def has_add_permission(self, request):
        return not AboutHero.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AboutSection2)
class AboutSection2Admin(admin.ModelAdmin):
    """Секція 2 - Про нас (PNG/SVG 4 версії - текстові поля)"""
    
    fieldsets = (
        ('🇺🇦 Україна - Світла тема', {
            'fields': ('image_ua_light',),
            'description': 'Вставте SVG код або PNG в форматі base64 (data:image/png;base64,...)'
        }),
        ('🇺🇦 Україна - Темна тема', {
            'fields': ('image_ua_dark',),
            'description': 'Вставте SVG код або PNG в форматі base64'
        }),
        ('🌍 Світ - Світла тема', {
            'fields': ('image_world_light',),
            'classes': ('collapse',),
            'description': 'Вставте SVG код або PNG в форматі base64'
        }),
        ('🌍 Світ - Темна тема', {
            'fields': ('image_world_dark',),
            'classes': ('collapse',),
            'description': 'Вставте SVG код або PNG в форматі base64'
        }),
        ('Налаштування', {
            'fields': ('is_active',)
        }),
    )
    
    def has_add_permission(self, request):
        return not AboutSection2.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AboutSection3)
class AboutSection3Admin(admin.ModelAdmin):
    """Секція 3 - Про нас (Заголовок + SVG)"""
    
    fieldsets = (
        ('🇺🇦 Заголовок Україна', {
            'fields': ('title_ua',)
        }),
        ('🇺🇦 SVG Україна - Світла', {
            'fields': ('svg_ua_light',)
        }),
        ('🇺🇦 SVG Україна - Темна', {
            'fields': ('svg_ua_dark',)
        }),
        ('🌍 Заголовок Світ', {
            'fields': ('title_world',),
            'classes': ('collapse',)
        }),
        ('🌍 SVG Світ - Світла', {
            'fields': ('svg_world_light',),
            'classes': ('collapse',)
        }),
        ('🌍 SVG Світ - Темна', {
            'fields': ('svg_world_dark',),
            'classes': ('collapse',)
        }),
        ('Налаштування', {
            'fields': ('is_active',)
        }),
    )
    
    def has_add_permission(self, request):
        return not AboutSection3.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AboutSection4)
class AboutSection4Admin(admin.ModelAdmin):
    """Секція 4 - Про нас (Заголовок + SVG)"""
    
    fieldsets = (
        ('🇺🇦 Заголовок Україна', {
            'fields': ('title_ua',)
        }),
        ('🇺🇦 SVG Україна - Світла', {
            'fields': ('svg_ua_light',)
        }),
        ('🇺🇦 SVG Україна - Темна', {
            'fields': ('svg_ua_dark',)
        }),
        ('🌍 Заголовок Світ', {
            'fields': ('title_world',),
            'classes': ('collapse',)
        }),
        ('🌍 SVG Світ - Світла', {
            'fields': ('svg_world_light',),
            'classes': ('collapse',)
        }),
        ('🌍 SVG Світ - Темна', {
            'fields': ('svg_world_dark',),
            'classes': ('collapse',)
        }),
        ('Налаштування', {
            'fields': ('is_active',)
        }),
    )
    
    def has_add_permission(self, request):
        return not AboutSection4.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


# ============================================
# 🎓 ХАБ ЗНАНЬ
# ============================================

@admin.register(HubHero)
class HubHeroAdmin(admin.ModelAdmin):
    """Hero секція - Хаб знань"""
    
    fieldsets = (
        ('Фонове зображення', {
            'fields': ('background_image',),
            'description': 'Завантажити фонове зображення для Hero секції'
        }),
        ('🇺🇦 Заголовок 1 (Україна)', {
            'fields': ('title_1_ua', 'subtitle_1_ua')
        }),
        ('🌍 Заголовок 1 (Світ)', {
            'fields': ('title_1_world', 'subtitle_1_world'),
            'classes': ('collapse',)
        }),
        ('🇺🇦 Заголовок 2 (Україна)', {
            'fields': ('title_2_ua', 'subtitle_2_ua')
        }),
        ('🌍 Заголовок 2 (Світ)', {
            'fields': ('title_2_world', 'subtitle_2_world'),
            'classes': ('collapse',)
        }),
        ('🇺🇦 Заголовок 3 (Україна)', {
            'fields': ('title_3_ua', 'subtitle_3_ua')
        }),
        ('🌍 Заголовок 3 (Світ)', {
            'fields': ('title_3_world', 'subtitle_3_world'),
            'classes': ('collapse',)
        }),
        ('Налаштування', {
            'fields': ('is_active',)
        }),
    )
    
    def has_add_permission(self, request):
        return not HubHero.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


# ============================================
# 💼 МЕНТОР КОУЧИНГ
# ============================================

@admin.register(MentorHero)
class MentorHeroAdmin(admin.ModelAdmin):
    """Hero блок - Ментор коучинг"""
    
    fieldsets = (
        ('Зображення', {
            'fields': ('image',),
            'description': 'Завантажити зображення для Hero блоку'
        }),
        ('Налаштування', {
            'fields': ('is_active',)
        }),
    )
    
    def has_add_permission(self, request):
        return not MentorHero.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MentorSection1Image)
class MentorSection1ImageAdmin(admin.ModelAdmin):
    """Секція 1 - 3 картинки (Ментор коучинг)"""
    list_display = ['position', 'caption_ua', 'is_active']
    list_editable = ['is_active']
    ordering = ['position']
    
    fieldsets = (
        ('Позиція', {
            'fields': ('position',),
            'description': 'Номер картинки: 1, 2 або 3'
        }),
        ('🇺🇦 Картинка Україна', {
            'fields': ('image_ua', 'caption_ua'),
            'description': '''
                <div style="background: #f0f8ff; padding: 12px; border-left: 4px solid #2196F3; margin: 10px 0;">
                    <p style="margin: 0;"><strong>📐 Рекомендований розмір:</strong> 800×500 px (формат 16:10)</p>
                    <p style="margin: 8px 0 0 0; color: #666; font-size: 0.9em;">
                        💡 Система автоматично адаптує зображення під картку, зберігаючи пропорції.
                    </p>
                </div>
            '''
        }),
        ('🌍 Картинка Світ', {
            'fields': ('image_world', 'caption_world'),
            'classes': ('collapse',)
        }),
        ('Налаштування', {
            'fields': ('is_active',)
        }),
    )


@admin.register(MentorSection2)
class MentorSection2Admin(admin.ModelAdmin):
    """Секція 2 - Ментор коучинг"""
    
    fieldsets = (
        ('🇺🇦 Заголовок Україна', {
            'fields': ('title_ua',)
        }),
        ('🇺🇦 SVG Україна - Світла', {
            'fields': ('svg_ua_light',)
        }),
        ('🇺🇦 SVG Україна - Темна', {
            'fields': ('svg_ua_dark',)
        }),
        ('🌍 Заголовок Світ', {
            'fields': ('title_world',),
            'classes': ('collapse',)
        }),
        ('🌍 SVG Світ - Світла', {
            'fields': ('svg_world_light',),
            'classes': ('collapse',)
        }),
        ('🌍 SVG Світ - Темна', {
            'fields': ('svg_world_dark',),
            'classes': ('collapse',)
        }),
        ('Налаштування', {
            'fields': ('is_active',)
        }),
    )
    
    def has_add_permission(self, request):
        return not MentorSection2.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MentorSection3)
class MentorSection3Admin(admin.ModelAdmin):
    """Секція 3 - Ментор коучинг (тільки SVG)"""
    
    fieldsets = (
        ('🇺🇦 SVG Україна - Світла', {
            'fields': ('svg_ua_light',)
        }),
        ('🇺🇦 SVG Україна - Темна', {
            'fields': ('svg_ua_dark',)
        }),
        ('🌍 SVG Світ - Світла', {
            'fields': ('svg_world_light',),
            'classes': ('collapse',)
        }),
        ('🌍 SVG Світ - Темна', {
            'fields': ('svg_world_dark',),
            'classes': ('collapse',)
        }),
        ('Налаштування', {
            'fields': ('is_active',)
        }),
    )
    
    def has_add_permission(self, request):
        return not MentorSection3.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MentorSection4)
class MentorSection4Admin(admin.ModelAdmin):
    """Секція 4 - Ментор + Команда"""
    
    fieldsets = (
        ('🇺🇦 Заголовок Україна', {
            'fields': ('title_ua', 'subtitle_ua'),
            'description': 'Після цієї секції показується Команда (ExpertCard)'
        }),
        ('🌍 Заголовок Світ', {
            'fields': ('title_world', 'subtitle_world'),
            'classes': ('collapse',)
        }),
        ('Налаштування', {
            'fields': ('is_active',)
        }),
    )
    
    def has_add_permission(self, request):
        return not MentorSection4.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


# ============================================
# 🏠 ГОЛОВНА - Ментор коучинг SVG
# ============================================

@admin.register(MentorCoachingSVG)
class MentorCoachingSVGAdmin(admin.ModelAdmin):
    """Ментор коучинг - Головна сторінка"""
    
    fieldsets = (
        ('🇺🇦 SVG Україна - Світла', {
            'fields': ('svg_ua_light',)
        }),
        ('🇺🇦 SVG Україна - Темна', {
            'fields': ('svg_ua_dark',)
        }),
        ('🌍 SVG Світ - Світла', {
            'fields': ('svg_world_light',),
            'classes': ('collapse',)
        }),
        ('🌍 SVG Світ - Темна', {
            'fields': ('svg_world_dark',),
            'classes': ('collapse',)
        }),
        ('Налаштування', {
            'fields': ('is_active',)
        }),
    )
    
    def has_add_permission(self, request):
        return not MentorCoachingSVG.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False

