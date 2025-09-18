from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from .models import (
    KnowledgeBase, AIQuery, AIPromptTemplate, 
    AIAccessPolicy, AIFeedback, AIConfiguration
)
from .services import KnowledgeBaseLoader


@admin.register(AIConfiguration)
class AIConfigurationAdmin(admin.ModelAdmin):
    list_display = ['llm_provider', 'llm_model', 'is_enabled', 'maintenance_mode', 'updated_at']
    list_filter = ['llm_provider', 'is_enabled', 'maintenance_mode']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('LLM Налаштування', {
            'fields': ('llm_provider', 'llm_model', 'api_key')
        }),
        ('Векторна База', {
            'fields': ('vector_store_provider', 'vector_store_config'),
            'classes': ('collapse',)
        }),
        ('Загальні Налаштування', {
            'fields': ('is_enabled', 'maintenance_mode', 'maintenance_message')
        }),
        ('Метадані', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('load-knowledge/', self.load_knowledge_view, name='ai_load_knowledge'),
            path('test-ai/', self.test_ai_view, name='ai_test'),
        ]
        return custom_urls + urls
    
    def load_knowledge_view(self, request):
        """Завантаження бази знань через admin"""
        if request.method == 'POST':
            try:
                loader = KnowledgeBaseLoader()
                knowledge_dir = settings.BASE_DIR / 'ai_knowledge_base'
                loaded_count = loader.load_from_directory(str(knowledge_dir))
                
                messages.success(request, f'Завантажено {loaded_count} документів в базу знань')
            except Exception as e:
                messages.error(request, f'Помилка завантаження: {str(e)}')
            
            return redirect('..')
        
        context = {
            'title': 'Завантаження бази знань',
            'total_entries': KnowledgeBase.objects.count(),
            'indexed_entries': KnowledgeBase.objects.filter(is_indexed=True).count(),
        }
        
        return render(request, 'admin/ai/load_knowledge.html', context)
    
    def test_ai_view(self, request):
        """Тестування AI через admin"""
        if request.method == 'POST':
            test_query = request.POST.get('test_query', 'Що таке Play Vision?')
            
            try:
                from .services import AIAgentService
                ai_service = AIAgentService()
                result = ai_service.process_query(test_query, request.user)
                
                return JsonResponse({
                    'success': result['success'],
                    'response': result['response'],
                    'sources': result.get('sources', []),
                    'response_time': result.get('response_time', 0)
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
        
        return render(request, 'admin/ai/test_ai.html', {
            'title': 'Тестування AI'
        })


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['title', 'content_type', 'access_level', 'is_indexed', 'created_at']
    list_filter = ['content_type', 'access_level', 'is_indexed']
    search_fields = ['title', 'content']
    readonly_fields = ['vector_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основна Інформація', {
            'fields': ('title', 'content_type', 'content_id')
        }),
        ('Контент', {
            'fields': ('content', 'metadata')
        }),
        ('Доступ', {
            'fields': ('access_level', 'is_indexed')
        }),
        ('Індексація', {
            'fields': ('vector_id',),
            'classes': ('collapse',)
        }),
        ('Метадані', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_for_indexing', 'remove_from_index']
    
    def mark_for_indexing(self, request, queryset):
        updated = queryset.update(is_indexed=True)
        self.message_user(request, f'{updated} записів позначено для індексації')
    mark_for_indexing.short_description = "Позначити для індексації"
    
    def remove_from_index(self, request, queryset):
        updated = queryset.update(is_indexed=False, vector_id='')
        self.message_user(request, f'{updated} записів видалено з індексу')
    remove_from_index.short_description = "Видалити з індексу"


@admin.register(AIQuery)
class AIQueryAdmin(admin.ModelAdmin):
    list_display = ['query_preview', 'user', 'user_access_level', 'user_rating', 'response_time_ms', 'created_at']
    list_filter = ['user_access_level', 'user_rating', 'created_at']
    search_fields = ['query', 'response']
    readonly_fields = ['query', 'response', 'context_sources', 'response_time_ms', 'tokens_used', 'created_at']
    
    def query_preview(self, obj):
        return obj.query[:50] + '...' if len(obj.query) > 50 else obj.query
    query_preview.short_description = 'Запит'
    
    def has_add_permission(self, request):
        return False  # Записи створюються автоматично
    
    def has_change_permission(self, request, obj=None):
        return False  # Записи read-only


@admin.register(AIPromptTemplate)
class AIPromptTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    
    fieldsets = (
        ('Основна Інформація', {
            'fields': ('name', 'description')
        }),
        ('Промпти', {
            'fields': ('system_prompt', 'user_prompt_template')
        }),
        ('Налаштування', {
            'fields': ('max_tokens', 'temperature', 'access_levels', 'is_active')
        })
    )


@admin.register(AIAccessPolicy)
class AIAccessPolicyAdmin(admin.ModelAdmin):
    list_display = ['level', 'max_response_length', 'access_premium_content', 'is_active']
    list_filter = ['level', 'is_active']
    
    fieldsets = (
        ('Рівень Доступу', {
            'fields': ('level',)
        }),
        ('Обмеження', {
            'fields': ('max_response_length', 'max_queries_per_day', 'max_queries_per_hour')
        }),
        ('Можливості', {
            'fields': ('include_links', 'show_previews', 'access_premium_content')
        }),
        ('Повідомлення', {
            'fields': ('cta_message',)
        }),
        ('Налаштування', {
            'fields': ('is_active',)
        })
    )


@admin.register(AIFeedback)
class AIFeedbackAdmin(admin.ModelAdmin):
    list_display = ['query', 'feedback_type', 'created_at']
    list_filter = ['feedback_type', 'created_at']
    readonly_fields = ['query', 'feedback_type', 'comment', 'created_at']
    
    def has_add_permission(self, request):
        return False
