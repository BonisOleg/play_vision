from django.contrib import admin
from django.db import models
from django.forms import TextInput
from .models import Category, Tag, Course, Material, UserCourseProgress, Favorite, MonthlyQuote


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'description', 'icon')}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'tag_type', 'display_order', 'created_at')
    list_filter = ('tag_type',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('tag_type', 'display_order', 'name')
    
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'tag_type', 'display_order')}),
    )


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
    list_display = ('title', 'category', 'difficulty', 'badge_type', 'price', 
                   'is_featured', 'is_published', 'view_count', 'enrollment_count', 'created_at')
    list_filter = ('category', 'difficulty', 'badge_type', 'content_type', 
                  'is_featured', 'is_free', 'is_classic', 'is_published', 
                  'requires_subscription', 'created_at')
    search_fields = ('title', 'slug', 'description', 'author')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    date_hierarchy = 'created_at'
    inlines = [MaterialInline]
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('title', 'slug', 'author', 'category', 'tags')
        }),
        ('Параметри курсу', {
            'fields': ('difficulty', 'content_type', 'target_audience', 
                      'training_specialization', 'duration_minutes')
        }),
        ('Опис', {
            'fields': ('short_description', 'description')
        }),
        ('Ціна та доступ', {
            'fields': ('price', 'is_free', 'requires_subscription', 'subscription_tiers')
        }),
        ('Медіа', {
            'fields': ('thumbnail', 'preview_video')
        }),
        ('Статус та відображення', {
            'fields': ('is_featured', 'badge_type', 'is_classic', 'is_published', 'published_at')
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
    list_display = ('title', 'course', 'content_type', 'order', 'is_preview', 'created_at')
    list_filter = ('content_type', 'is_preview', 'created_at')
    search_fields = ('title', 'course__title')
    raw_id_fields = ('course',)
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('course', 'order')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('course', 'title', 'slug', 'content_type', 'order')
        }),
        ('Content', {
            'fields': ('video_file', 'video_duration_seconds', 'pdf_file', 'article_content')
        }),
        ('Preview Settings', {
            'fields': ('is_preview', 'preview_seconds', 'preview_percentage')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


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