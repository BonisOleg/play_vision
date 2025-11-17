from django.contrib import admin
from .models import AIConfiguration, AIKnowledgeDocument


@admin.register(AIConfiguration)
class AIConfigurationAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'is_enabled', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Налаштування', {
            'fields': ('api_key', 'is_enabled'),
            'description': 'API ключ для інтеграції з AI сервісом'
        }),
        ('Метадані', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def has_add_permission(self, request):
        # Дозволити створити тільки якщо не існує
        return not AIConfiguration.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AIKnowledgeDocument)
class AIKnowledgeDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'file_type', 'is_indexed', 'created_at']
    list_filter = ['file_type', 'is_indexed', 'created_at']
    list_editable = ['is_indexed']
    search_fields = ['title']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Документ', {
            'fields': ('title', 'file', 'file_type'),
            'description': 'Завантажте PDF або TXT документ для бази знань AI'
        }),
        ('Статус', {
            'fields': ('is_indexed',),
        }),
        ('Метадані', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
