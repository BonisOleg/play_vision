from django.db import models
from django.utils import timezone


def check_user_course_access(user, course):
    """
    Check if user has access to a specific course
    TODO: Оновити для нової системи підписок
    """
    if not user or not user.is_authenticated:
        return False
    
    # Free courses are available to all authenticated users
    if course.is_free:
        return True
    
    # Check if user purchased the course individually
    from apps.payments.models import Payment, OrderItem
    purchased = Payment.objects.filter(
        user=user,
        status='succeeded',
        order__items__item_type='course',
        order__items__item_id=course.id
    ).exists()
    
    if purchased:
        return True
    
    # TODO: Check if course requires subscription (нова система)
    # if course.requires_subscription:
    #     active_subscriptions = user.subscriptions.filter(...)
    #     ...
    
    return False


def get_user_accessible_courses(user):
    """
    Get all courses accessible by user
    TODO: Оновити для нової системи підписок
    """
    from apps.content.models import Course
    
    if not user or not user.is_authenticated:
        # Only free courses for non-authenticated
        return Course.objects.filter(is_free=True, is_published=True)
    
    # Start with free courses
    accessible_courses = Course.objects.filter(is_free=True, is_published=True)
    
    # Add individually purchased courses
    from apps.payments.models import Payment
    purchased_course_ids = Payment.objects.filter(
        user=user,
        status='succeeded'
    ).values_list('order__items__item_id', flat=True).distinct()
    
    purchased_courses = Course.objects.filter(id__in=purchased_course_ids, is_published=True)
    
    # TODO: Add subscription courses (нова система)
    # active_subscriptions = user.subscriptions.filter(...)
    # if active_subscriptions.exists():
    #     subscription_courses = ...
    #     accessible_courses = accessible_courses | purchased_courses | subscription_courses
    # else:
    #     accessible_courses = accessible_courses | purchased_courses
    
    accessible_courses = accessible_courses | purchased_courses
    
    return accessible_courses.distinct()


def calculate_content_preview_limits(content_type, content):
    """
    Calculate preview limits for different content types
    """
    if content_type == 'video':
        # 20 seconds preview for video
        return {
            'preview_seconds': 20,
            'preview_url': content.preview_video.url if content.preview_video else None
        }
    elif content_type == 'pdf':
        # 10% preview for PDF (first N pages)
        if hasattr(content, 'pdf_file') and content.pdf_file:
            # This would need PDF processing logic
            return {
                'preview_percentage': 10,
                'preview_pages': 2  # Or calculate based on total pages
            }
    elif content_type == 'article':
        # 10% preview for articles (character count)
        if hasattr(content, 'article_content'):
            total_length = len(content.article_content)
            preview_length = int(total_length * 0.1)
            return {
                'preview_percentage': 10,
                'preview_characters': preview_length,
                'preview_text': content.article_content[:preview_length]
            }
    
    return {}
