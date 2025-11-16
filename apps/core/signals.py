"""
Signal handlers for audit trail and versioning
Auto-tracks all model changes
"""
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save)
def track_changes(sender, instance, **kwargs):
    """
    Track field changes before save
    Stores changes in instance._tracked_changes for later use
    """
    # Skip if new object (no previous state to compare)
    if instance._state.adding:
        return
    
    # Skip AuditLog and ContentVersion to avoid recursion
    if sender.__name__ in ['AuditLog', 'ContentVersion', 'LogEntry']:
        return
    
    try:
        # Get old version from database
        old_instance = sender.objects.get(pk=instance.pk)
        changes = {}
        
        # Compare all fields
        for field in instance._meta.fields:
            field_name = field.name
            
            # Skip auto-generated fields
            if field_name in ['updated_at', 'last_login']:
                continue
            
            old_value = getattr(old_instance, field_name, None)
            new_value = getattr(instance, field_name, None)
            
            # Convert to string for comparison
            old_str = str(old_value) if old_value is not None else ''
            new_str = str(new_value) if new_value is not None else ''
            
            if old_str != new_str:
                changes[field_name] = {
                    'old': old_str[:200],  # Truncate long values
                    'new': new_str[:200]
                }
        
        # Store changes on instance
        instance._tracked_changes = changes
        
    except sender.DoesNotExist:
        # Object doesn't exist yet (shouldn't happen with pre_save)
        pass
    except Exception as e:
        logger.error(f"Error tracking changes for {sender.__name__}: {e}")


@receiver(post_save)
def log_save_action(sender, instance, created, **kwargs):
    """
    Log create/update actions to audit trail
    """
    # Skip certain models to avoid recursion
    if sender.__name__ in ['AuditLog', 'ContentVersion', 'LogEntry', 'Session']:
        return
    
    try:
        from apps.core.models import AuditLog
        from apps.core.services import get_current_request
        
        # Get current request from thread-local storage
        request = get_current_request()
        
        # Determine action
        action = 'create' if created else 'update'
        
        # Get tracked changes (if any)
        changes = getattr(instance, '_tracked_changes', {})
        
        # Create audit log entry
        AuditLog.objects.create(
            user=request.user if request and request.user.is_authenticated else None,
            content_type=ContentType.objects.get_for_model(sender),
            object_id=instance.pk,
            object_repr=str(instance)[:200],
            action=action,
            changes=changes,
            ip_address=getattr(request, 'client_ip', None) if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500] if request else ''
        )
        
        logger.debug(f"Audit log created: {action} {sender.__name__} #{instance.pk}")
        
    except Exception as e:
        # Don't break the save operation if audit logging fails
        logger.error(f"Failed to create audit log for {sender.__name__}: {e}")


@receiver(post_delete)
def log_delete_action(sender, instance, **kwargs):
    """
    Log delete actions to audit trail
    """
    # Skip certain models
    if sender.__name__ in ['AuditLog', 'ContentVersion', 'LogEntry', 'Session']:
        return
    
    try:
        from apps.core.models import AuditLog
        from apps.core.services import get_current_request
        
        request = get_current_request()
        
        AuditLog.objects.create(
            user=request.user if request and request.user.is_authenticated else None,
            content_type=ContentType.objects.get_for_model(sender),
            object_id=instance.pk,
            object_repr=str(instance)[:200],
            action='delete',
            changes={},
            ip_address=getattr(request, 'client_ip', None) if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500] if request else ''
        )
        
        logger.debug(f"Audit log created: delete {sender.__name__} #{instance.pk}")
        
    except Exception as e:
        logger.error(f"Failed to log deletion of {sender.__name__}: {e}")


# Auto-load signals when app is ready
def setup_signals():
    """
    Call this from AppConfig.ready() to ensure signals are connected
    """
    logger.info("Audit trail signals registered")

