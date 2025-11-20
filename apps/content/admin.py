from django.contrib import admin
from django.db import models
from django.forms import TextInput, CheckboxSelectMultiple
from django import forms
import json
from .models import Course, Material, UserCourseProgress, Favorite, MonthlyQuote


class CourseAdminForm(forms.ModelForm):
    target_audience = forms.MultipleChoiceField(
        choices=Course.TARGET_AUDIENCE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Кому підходить'
    )
    
    class Meta:
        model = Course
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if isinstance(self.instance.target_audience, list):
                self.initial['target_audience'] = self.instance.target_audience
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.target_audience = self.cleaned_data.get('target_audience', [])
        if commit:
            instance.save()
        return instance


class MaterialInline(admin.TabularInline):
    model = Material
    extra = 0
    fields = ('title', 'slug', 'content_type', 'order', 'is_preview')
    prepopulated_fields = {'slug': ('title',)}
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '20'})},
    }


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Курси 🧪 BETA"""
    form = CourseAdminForm
    list_display = ('title', 'price', 'is_featured', 'is_published', 
                   'view_count', 'enrollment_count', 'created_at')
    list_filter = ('is_featured', 'is_free', 'is_published', 
                  'requires_subscription', 'created_at')
    search_fields = ('title', 'slug', 'description', 'author')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    inlines = [MaterialInline]
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('title', 'slug', 'author', 'target_audience')
        }),
        ('Опис', {
            'fields': ('short_description', 'description')
        }),
        ('Ціна та доступ', {
            'fields': ('price', 'is_free', 'requires_subscription', 'subscription_tiers')
        }),
        ('Медіа', {
            'fields': ('thumbnail', 'logo', 'preview_video')
        }),
        ('Статус та відображення', {
            'fields': ('is_featured', 'is_published', 'published_at')
        }),
        ('Статистика', {
            'fields': ('view_count', 'enrollment_count', 'rating'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Часові мітки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('view_count', 'enrollment_count', 'rating', 'created_at', 'updated_at')
    
    actions = ['make_featured', 'remove_featured', 'publish', 'unpublish']
    
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)
    make_featured.short_description = "Mark selected courses as featured"
    
    def remove_featured(self, request, queryset):
        queryset.update(is_featured=False)
    remove_featured.short_description = "Remove featured status"
    
    def publish(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_published=True, published_at=timezone.now())
    publish.short_description = "Publish selected courses"
    
    def unpublish(self, request, queryset):
        queryset.update(is_published=False)
    unpublish.short_description = "Unpublish selected courses"


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'content_type', 'video_source', 'order', 
                   'is_preview', 'bunny_status_display', 'created_at')
    list_filter = ('content_type', 'video_source', 'is_preview', 'created_at')
    search_fields = ('title', 'course__title', 'bunny_video_id')
    raw_id_fields = ('course',)
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('course', 'order')
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('course', 'title', 'slug', 'content_type', 'order')
        }),
        ('Контент (Локальне зберігання)', {
            'fields': ('video_file', 'video_duration_seconds', 'pdf_file', 'article_content'),
            'classes': ('collapse',)
        }),
        ('Bunny.net CDN', {
            'fields': ('video_source', 'bunny_video_id', 'bunny_collection_id', 
                      'bunny_video_status', 'bunny_thumbnail_url'),
            'description': 'Налаштування для відео з Bunny.net CDN'
        }),
        ('Налаштування превʼю', {
            'fields': ('is_preview', 'preview_seconds', 'preview_percentage')
        }),
        ('Захист відео (застаріле)', {
            'fields': ('secure_video_enabled', 's3_video_key', 'video_access_token', 'token_expires_at'),
            'classes': ('collapse',)
        }),
        ('Часові мітки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'bunny_video_status', 'bunny_thumbnail_url')
    
    actions = ['upload_to_bunny']
    
    def bunny_status_display(self, obj):
        """Відображення статусу Bunny.net відео"""
        if obj.video_source == 'bunny' and obj.bunny_video_id:
            status_map = {
                '0': '⏳ В черзі',
                '1': '🔄 Обробка',
                '2': '📦 Кодування',
                '3': '✅ Готово',
                '4': '❌ Помилка',
                '5': '🗑️ Видалено',
                '6': '⏸️ Призупинено',
            }
            status = obj.bunny_video_status or '0'
            return status_map.get(status, f'Статус {status}')
        return '-'
    bunny_status_display.short_description = 'Bunny статус'
    
    def upload_to_bunny(self, request, queryset):
        """Масове завантаження відео на Bunny.net"""
        from apps.video_security.bunny_service import BunnyService
        from django.contrib import messages
        
        if not BunnyService.is_enabled():
            messages.error(request, 'Bunny.net інтеграція вимкнена в налаштуваннях')
            return
        
        success_count = 0
        error_count = 0
        
        for material in queryset.filter(content_type='video'):
            # Перевірити чи є локальний файл
            if not material.video_file:
                error_count += 1
                continue
            
            try:
                # Завантажити на Bunny.net
                video_data = BunnyService.upload_video(
                    file_path=material.video_file.path,
                    title=material.title,
                    collection_id=material.course.slug  # Використовуємо slug курсу як колекцію
                )
                
                if video_data:
                    # Оновити матеріал
                    material.video_source = 'bunny'
                    material.bunny_video_id = video_data.get('guid')
                    material.bunny_video_status = str(video_data.get('status', '0'))
                    material.save()
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                error_count += 1
                continue
        
        if success_count:
            messages.success(request, f'Успішно завантажено {success_count} відео на Bunny.net')
        if error_count:
            messages.error(request, f'Помилка завантаження {error_count} відео')
    
    upload_to_bunny.short_description = '📤 Завантажити відео на Bunny.net CDN'


@admin.register(UserCourseProgress)
class UserCourseProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'progress_percentage', 'started_at', 
                   'last_accessed', 'completed_at')
    list_filter = ('completed_at', 'started_at')
    search_fields = ('user__email', 'course__title')
    raw_id_fields = ('user', 'course')
    filter_horizontal = ('materials_completed',)
    readonly_fields = ('started_at', 'last_accessed', 'completed_at')
    
    def has_add_permission(self, request):
        # Progress records should be created automatically
        return False


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'course__title')
    raw_id_fields = ('user', 'course')
    readonly_fields = ('created_at',)


@admin.register(MonthlyQuote)
class MonthlyQuoteAdmin(admin.ModelAdmin):
    list_display = ['expert_name', 'expert_role', 'month', 'is_active', 'views_count']
    list_filter = ['is_active', 'month']
    search_fields = ['expert_name', 'expert_role', 'quote_text']
    date_hierarchy = 'month'
    readonly_fields = ['views_count', 'last_displayed_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Експерт', {
            'fields': ('expert_name', 'expert_role', 'expert_photo')
        }),
        ('Цитата', {
            'fields': ('quote_text', 'month', 'is_active')
        }),
        ('Статистика', {
            'fields': ('views_count', 'last_displayed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Очистити кеш при збереженні
        from django.core.cache import cache
        cache.delete('current_monthly_quote')
        super().save_model(request, obj, form, change)