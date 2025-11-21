"""
Core models - Abstract base classes for DRY principle
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Abstract base model with created_at and updated_at timestamps
    
    Usage:
        class MyModel(TimeStampedModel):
            name = models.CharField(max_length=100)
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='Timestamp when object was created'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp when object was last updated'
    )
    
    class Meta:
        abstract = True
        ordering = ['-created_at']


class VersionedContentModel(TimeStampedModel):
    """
    Abstract base model for content with Ukraine/World versions
    
    Ukraine version is primary and NEVER blank.
    World version is optional fallback.
    
    Usage:
        class MyContent(VersionedContentModel):
            image = models.ImageField(...)
    """
    # Ukraine version (primary) - NEVER blank
    title_ua = models.CharField(
        max_length=200,
        verbose_name='Title (Ukraine)',
        help_text='Primary title in Ukrainian - always shown in Ukraine'
    )
    content_ua = models.TextField(
        blank=True,
        verbose_name='Content (Ukraine)',
        help_text='Primary content in Ukrainian'
    )
    
    # World version (fallback) - can be blank
    title_world = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Title (World)',
        help_text='Alternative title for non-Ukraine regions - if empty, shows UA version'
    )
    content_world = models.TextField(
        blank=True,
        verbose_name='Content (World)',
        help_text='Alternative content for non-Ukraine regions'
    )
    
    class Meta:
        abstract = True
    
    def get_title(self, country_code='UA'):
        """
        Get title by country code with automatic fallback
        
        Args:
            country_code: 2-letter ISO country code (e.g. 'UA', 'US', 'GB')
        
        Returns:
            str: Title in appropriate language
        """
        if country_code == 'UA' or not self.title_world:
            return self.title_ua
        return self.title_world
    
    def get_content(self, country_code='UA'):
        """
        Get content by country code with automatic fallback
        
        Args:
            country_code: 2-letter ISO country code
        
        Returns:
            str: Content in appropriate language
        """
        if country_code == 'UA' or not self.content_world:
            return self.content_ua
        return self.content_world


class AuditedModel(TimeStampedModel):
    """
    Abstract base model with full audit trail
    
    Tracks who created and last updated the object.
    Use with signals for complete change history.
    
    Usage:
        class MyModel(AuditedModel):
            name = models.CharField(max_length=100)
    """
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        verbose_name='Created by',
        help_text='User who created this object'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        verbose_name='Last updated by',
        help_text='User who last updated this object'
    )
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        """Override save to track user from request context"""
        # User will be set via middleware or admin
        super().save(*args, **kwargs)


class LegalPage(TimeStampedModel):
    """
    Legal documents (Privacy Policy, Terms of Service, Offer)
    
    Singleton-like: slug determines the document type.
    Content stored in HTML for rich formatting.
    """
    SLUG_CHOICES = [
        ('privacy', 'Політика конфіденційності'),
        ('terms', 'Умови використання'),
        ('offer', 'Публічна оферта'),
    ]
    
    slug = models.CharField(
        max_length=50,
        unique=True,
        choices=SLUG_CHOICES,
        verbose_name='Тип документа',
        help_text='URL-ключ документа'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок',
        help_text='Заголовок документа'
    )
    content = models.TextField(
        verbose_name='Зміст',
        help_text='Повний текст документа (HTML дозволено)'
    )
    version_date = models.DateField(
        default=timezone.now,
        verbose_name='Дата редакції',
        help_text='Дата поточної редакції документа'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активний',
        help_text='Показувати документ на сайті'
    )
    
    class Meta:
        db_table = 'core_legal_pages'
        verbose_name = 'Юридичний документ'
        verbose_name_plural = '📋 Юридичні документи'
        ordering = ['slug']
    
    def __str__(self):
        return f"{self.get_slug_display()} ({self.version_date})"


class AuditLog(TimeStampedModel):
    """
    Audit trail for all admin changes
    
    Automatically populated via signals.
    Never delete - immutable history.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='User',
        help_text='User who performed the action'
    )
    
    # Generic foreign key to any model
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    object_repr = models.CharField(
        max_length=200,
        help_text='String representation of the object'
    )
    
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
    ]
    action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES,
        db_index=True
    )
    
    # Change details
    changes = models.JSONField(
        default=dict,
        help_text='Field changes: {"field": {"old": "...", "new": "..."}}'
    )
    
    # Request context
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP address of the user'
    )
    user_agent = models.TextField(
        blank=True,
        help_text='Browser user agent string'
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='When the action occurred'
    )
    
    class Meta:
        db_table = 'core_audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user} {self.action} {self.object_repr} at {self.timestamp}"


class ContentVersion(TimeStampedModel):
    """
    Version history for CMS content
    
    Stores complete snapshot of object state for rollback capability.
    """
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    
    version_number = models.PositiveIntegerField(
        help_text='Sequential version number'
    )
    snapshot = models.JSONField(
        help_text='Complete serialized object state'
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Created by'
    )
    change_summary = models.TextField(
        blank=True,
        help_text='Optional summary of changes in this version'
    )
    
    class Meta:
        db_table = 'cms_content_versions'
        verbose_name = 'Content Version'
        verbose_name_plural = 'Content Versions'
        ordering = ['-version_number']
        unique_together = [('content_type', 'object_id', 'version_number')]
        indexes = [
            models.Index(fields=['content_type', 'object_id', '-version_number']),
            models.Index(fields=['created_by', '-created_at']),
        ]
    
    def __str__(self):
        return f"v{self.version_number} of {self.content_type} #{self.object_id}"
    
    @classmethod
    def create_version(cls, instance, user=None, summary=''):
        """
        Create version snapshot of an instance
        
        Args:
            instance: Django model instance to snapshot
            user: User making the change
            summary: Optional description of changes
        
        Returns:
            ContentVersion: Created version object
        """
        from django.core import serializers
        from django.contrib.contenttypes.models import ContentType
        
        ct = ContentType.objects.get_for_model(instance)
        
        # Get latest version number
        latest = cls.objects.filter(
            content_type=ct,
            object_id=instance.pk
        ).aggregate(models.Max('version_number'))['version_number__max'] or 0
        
        # Serialize instance
        snapshot_data = serializers.serialize('json', [instance])
        
        return cls.objects.create(
            content_type=ct,
            object_id=instance.pk,
            version_number=latest + 1,
            snapshot=snapshot_data,
            created_by=user,
            change_summary=summary
        )
