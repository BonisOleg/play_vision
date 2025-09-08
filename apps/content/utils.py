from django.db import models
from django.utils import timezone


def check_user_course_access(user, course):
    """
    Check if user has access to a specific course
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
    
    # Check if course requires subscription
    if course.requires_subscription:
        # Get active subscriptions
        active_subscriptions = user.subscriptions.filter(
            status='active',
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        )
        
        for subscription in active_subscriptions:
            # Check if subscription tier is allowed for this course
            if not course.subscription_tiers or subscription.plan.slug in course.subscription_tiers:
                return True
    
    return False


def get_user_accessible_courses(user):
    """
    Get all courses accessible by user
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
    
    # Add subscription courses
    active_subscriptions = user.subscriptions.filter(
        status='active',
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    )
    
    if active_subscriptions.exists():
        # Get subscription tiers
        subscription_tiers = list(active_subscriptions.values_list('plan__slug', flat=True))
        
        # Get courses available for these tiers
        from django.db import connection
        
        if connection.vendor == 'postgresql':
            # PostgreSQL specific operations
            subscription_courses = Course.objects.filter(
                requires_subscription=True,
                is_published=True
            ).filter(
                models.Q(subscription_tiers__len=0) |  # No tier restrictions
                models.Q(subscription_tiers__overlap=subscription_tiers)  # Tier matches
            )
        else:
            # SQLite compatible version
            subscription_courses = Course.objects.filter(
                requires_subscription=True,
                is_published=True
            )
            
            # Фільтрування в Python для SQLite
            filtered_courses = []
            for course in subscription_courses:
                # Якщо немає обмежень по рівнях підписки
                if not course.subscription_tiers:
                    filtered_courses.append(course.id)
                # Або якщо є перетин з доступними рівнями
                elif any(tier in course.subscription_tiers for tier in subscription_tiers):
                    filtered_courses.append(course.id)
            
            subscription_courses = Course.objects.filter(id__in=filtered_courses)
        
        # Combine all accessible courses
        accessible_courses = accessible_courses | purchased_courses | subscription_courses
    else:
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
