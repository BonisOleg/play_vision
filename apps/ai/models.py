from django.db import models
from django.conf import settings


class AIConfiguration(models.Model):
    """
    Налаштування AI-системи (спрощена версія)
    """
    api_key = models.CharField(max_length=200, blank=True, verbose_name='API ключ')
    is_enabled = models.BooleanField(default=True, verbose_name='Активовано')
    
    # Метадані
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_configuration'
        verbose_name = 'Налаштування AI'
        verbose_name_plural = 'Налаштування AI'
    
    def __str__(self):
        return f"AI Configuration - {'Enabled' if self.is_enabled else 'Disabled'}"
    
    def save(self, *args, **kwargs):
        # Тільки один екземпляр
        self.pk = 1
        super().save(*args, **kwargs)


class AIKnowledgeDocument(models.Model):
    """
    Документи для бази знань AI (PDF/TXT)
    """
    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('txt', 'TXT'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Назва')
    file = models.FileField(upload_to='ai/knowledge/', verbose_name='Файл', max_length=500)
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, verbose_name='Тип файлу')
    is_indexed = models.BooleanField(default=False, verbose_name='Проіндексовано')
    
    # Метадані
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_knowledge_documents'
        verbose_name = 'Документ бази знань'
        verbose_name_plural = 'База знань'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_file_type_display()})"
