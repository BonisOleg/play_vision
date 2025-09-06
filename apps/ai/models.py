from django.db import models
from django.conf import settings
from django.utils import timezone


class KnowledgeBase(models.Model):
    """
    База знань для AI-агента
    """
    CONTENT_TYPES = [
        ('course', 'Курс'),
        ('lesson', 'Урок'),
        ('article', 'Стаття'),
        ('faq', 'FAQ'),
        ('manual', 'Інструкція'),
    ]
    
    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content_id = models.PositiveIntegerField(null=True, blank=True, 
                                           help_text='ID пов\'язаного контенту')
    
    # Контент для індексації
    content = models.TextField(help_text='Текст для векторного пошуку')
    metadata = models.JSONField(default=dict, help_text='Додаткові метадані')
    
    # Права доступу
    access_level = models.CharField(max_length=20, choices=[
        ('public', 'Публічний'),
        ('registered', 'Зареєстровані'),
        ('subscriber', 'Підписники'),
        ('premium', 'Преміум'),
    ], default='public')
    
    # Індексація
    is_indexed = models.BooleanField(default=False)
    vector_id = models.CharField(max_length=100, blank=True, 
                               help_text='ID у векторній базі')
    
    # Метадані
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_knowledge_base'
        verbose_name = 'Knowledge Base Entry'
        verbose_name_plural = 'Knowledge Base Entries'
        indexes = [
            models.Index(fields=['content_type', 'content_id']),
            models.Index(fields=['access_level']),
        ]
    
    def __str__(self):
        return self.title


class AIQuery(models.Model):
    """
    Запити користувачів до AI-агента
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                           related_name='ai_queries', null=True, blank=True)
    session_id = models.CharField(max_length=100, help_text='ID сесії для анонімних користувачів')
    
    # Запит та відповідь
    query = models.TextField(help_text='Запит користувача')
    response = models.TextField(help_text='Відповідь AI')
    
    # Контекст
    user_access_level = models.CharField(max_length=20, default='guest')
    context_sources = models.JSONField(default=list, 
                                     help_text='Джерела, використані для відповіді')
    
    # Метрики
    response_time_ms = models.PositiveIntegerField(help_text='Час відгуку в мілісекундах')
    tokens_used = models.PositiveIntegerField(default=0)
    
    # Оцінка користувача
    user_rating = models.PositiveIntegerField(null=True, blank=True,
                                            help_text='Оцінка від 1 до 5')
    user_feedback = models.TextField(blank=True)
    
    # Метадані
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_queries'
        verbose_name = 'AI Query'
        verbose_name_plural = 'AI Queries'
        ordering = ['-created_at']
    
    def __str__(self):
        user_info = self.user.email if self.user else f"Session {self.session_id}"
        return f"{user_info}: {self.query[:50]}..."


class AIPromptTemplate(models.Model):
    """
    Шаблони промптів для різних типів запитів
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(help_text='Опис призначення шаблону')
    
    # Шаблон
    system_prompt = models.TextField(help_text='Системний промпт')
    user_prompt_template = models.TextField(help_text='Шаблон користувацького промпту з плейсхолдерами')
    
    # Налаштування
    max_tokens = models.PositiveIntegerField(default=1000)
    temperature = models.FloatField(default=0.7, help_text='Творчість відповіді (0-1)')
    
    # Умови використання
    access_levels = models.JSONField(default=list, 
                                   help_text='Рівні доступу, для яких доступний шаблон')
    
    # Метадані
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_prompt_templates'
        verbose_name = 'AI Prompt Template'
        verbose_name_plural = 'AI Prompt Templates'
    
    def __str__(self):
        return self.name


class AIAccessPolicy(models.Model):
    """
    Політики доступу для AI-відповідей
    """
    ACCESS_LEVELS = [
        ('guest', 'Гість'),
        ('registered', 'Зареєстрований'),
        ('subscriber_l1', 'Підписник L1'),
        ('subscriber_l2', 'Підписник L2'),
        ('admin', 'Адміністратор'),
    ]
    
    level = models.CharField(max_length=20, choices=ACCESS_LEVELS, unique=True)
    
    # Обмеження відповідей
    max_response_length = models.PositiveIntegerField(help_text='Максимальна довжина відповіді')
    max_queries_per_day = models.PositiveIntegerField(help_text='Максимум запитів на день')
    max_queries_per_hour = models.PositiveIntegerField(help_text='Максимум запитів на годину')
    
    # Можливості
    include_links = models.BooleanField(default=False, help_text='Чи включати посилання')
    show_previews = models.BooleanField(default=False, help_text='Чи показувати превью контенту')
    access_premium_content = models.BooleanField(default=False, 
                                               help_text='Доступ до преміум контенту')
    
    # Повідомлення
    cta_message = models.CharField(max_length=200, blank=True, 
                                 help_text='Повідомлення з закликом до дії')
    
    # Налаштування
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'ai_access_policies'
        verbose_name = 'AI Access Policy'
        verbose_name_plural = 'AI Access Policies'
    
    def __str__(self):
        return f"Policy for {self.get_level_display()}"


class AIFeedback(models.Model):
    """
    Відгуки користувачів про якість AI-відповідей
    """
    FEEDBACK_TYPES = [
        ('helpful', 'Корисно'),
        ('not_helpful', 'Не корисно'),
        ('incorrect', 'Неправильно'),
        ('incomplete', 'Неповно'),
        ('offensive', 'Образливо'),
    ]
    
    query = models.ForeignKey(AIQuery, on_delete=models.CASCADE, related_name='feedback')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    comment = models.TextField(blank=True, help_text='Додатковий коментар')
    
    # Метадані
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_feedback'
        verbose_name = 'AI Feedback'
        verbose_name_plural = 'AI Feedback'
        unique_together = ['query', 'feedback_type']
    
    def __str__(self):
        return f"{self.get_feedback_type_display()} for query #{self.query.id}"


class AIConfiguration(models.Model):
    """
    Глобальні налаштування AI-системи
    """
    # LLM налаштування
    llm_provider = models.CharField(max_length=50, default='openai', 
                                  choices=[
                                      ('openai', 'OpenAI'),
                                      ('anthropic', 'Anthropic'),
                                      ('local', 'Local Model'),
                                  ])
    llm_model = models.CharField(max_length=100, default='gpt-3.5-turbo')
    api_key = models.CharField(max_length=200, blank=True)
    
    # Векторна база
    vector_store_provider = models.CharField(max_length=50, default='chroma',
                                           choices=[
                                               ('chroma', 'ChromaDB'),
                                               ('pinecone', 'Pinecone'),
                                               ('weaviate', 'Weaviate'),
                                           ])
    vector_store_config = models.JSONField(default=dict)
    
    # Загальні налаштування
    is_enabled = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.CharField(max_length=200, blank=True)
    
    # Метадані
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_configuration'
        verbose_name = 'AI Configuration'
        verbose_name_plural = 'AI Configuration'
    
    def __str__(self):
        return f"AI Config - {self.llm_provider}/{self.llm_model}"