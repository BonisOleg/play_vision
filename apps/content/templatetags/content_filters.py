from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.text import Truncator

register = template.Library()

@register.filter
def truncate_chars(value, max_length):
    """
    Truncate a string after a certain number of characters.
    """
    if not value:
        return value
    
    max_length = int(max_length)
    if len(value) <= max_length:
        return value
    
    return value[:max_length] + '...'


@register.filter
def duration_format(minutes):
    """
    Convert minutes to human-readable format.
    """
    if not minutes:
        return ''
    
    hours = minutes // 60
    mins = minutes % 60
    
    if hours:
        return f"{hours}г {mins}хв"
    return f"{mins}хв"


@register.filter
def percentage_of(value, total):
    """
    Calculate percentage of value from total.
    """
    if not total or total == 0:
        return 0
    
    try:
        value = float(value)
        total = float(total)
        return round((value / total) * 100, 1)
    except (ValueError, TypeError):
        return 0


@register.filter
def has_access_to_course(user, course):
    """
    Check if user has access to course.
    """
    if not user or not user.is_authenticated:
        return False
    
    from apps.content.utils import check_user_course_access
    return check_user_course_access(user, course)


@register.simple_tag
def course_progress_percentage(user, course):
    """
    Get course progress percentage for user.
    """
    if not user or not user.is_authenticated:
        return 0
    
    try:
        from apps.content.models import UserCourseProgress
        progress = UserCourseProgress.objects.get(user=user, course=course)
        return round(progress.progress_percentage, 1)
    except UserCourseProgress.DoesNotExist:
        return 0


@register.simple_tag
def material_completed(user, material):
    """
    Check if material is completed by user.
    """
    if not user or not user.is_authenticated:
        return False
    
    try:
        from apps.content.models import UserCourseProgress
        progress = UserCourseProgress.objects.get(user=user, course=material.course)
        return material in progress.materials_completed.all()
    except UserCourseProgress.DoesNotExist:
        return False


@register.filter
def video_duration_display(seconds):
    """
    Convert seconds to MM:SS format.
    """
    if not seconds:
        return '0:00'
    
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    
    return f"{minutes}:{secs:02d}"


@register.filter
def content_preview_text(content, percentage=10):
    """
    Get preview text based on percentage.
    """
    if not content:
        return ''
    
    try:
        percentage = int(percentage)
        total_length = len(content)
        preview_length = int(total_length * (percentage / 100))
        
        if preview_length >= total_length:
            return content
        
        # Try to cut at word boundary
        preview = content[:preview_length]
        last_space = preview.rfind(' ')
        
        if last_space > preview_length * 0.8:  # If we can cut at word boundary
            preview = preview[:last_space]
        
        return preview + '...'
    except (ValueError, TypeError):
        return content


@register.simple_tag
def content_access_status(user, course):
    """
    Get content access status for course.
    Returns: 'full', 'preview', 'locked'
    """
    if not course:
        return 'locked'
    
    # Check if course is free
    if course.is_free:
        return 'full'
    
    # Check user access
    if user and user.is_authenticated:
        from apps.content.utils import check_user_course_access
        if check_user_course_access(user, course):
            return 'full'
    
    # Check if preview is available
    if hasattr(course, 'preview_video') and course.preview_video:
        return 'preview'
    
    return 'locked'


@register.inclusion_tag('partials/course_card.html')
def course_card(course, user=None, show_favorites=True, show_progress=True):
    """
    Render course card with access information.
    """
    context = {
        'course': course,
        'user': user,
        'show_favorites': show_favorites,
        'show_progress': show_progress,
    }
    
    if user and user.is_authenticated:
        # Check if favorited
        try:
            from apps.content.models import Favorite
            context['is_favorite'] = Favorite.objects.filter(
                user=user, course=course
            ).exists()
        except:
            context['is_favorite'] = False
        
        # Get progress if requested
        if show_progress:
            try:
                from apps.content.models import UserCourseProgress
                progress = UserCourseProgress.objects.get(user=user, course=course)
                context['progress'] = progress
            except UserCourseProgress.DoesNotExist:
                context['progress'] = None
    else:
        context['is_favorite'] = False
        context['progress'] = None
    
    # Access status
    context['access_status'] = content_access_status(user, course)
    
    return context


@register.filter
def add_css_class(field, css_class):
    """
    Add CSS class to form field.
    """
    return field.as_widget(attrs={'class': css_class})


@register.simple_tag
def query_string(request, **kwargs):
    """
    Update query string with new parameters.
    """
    query_dict = request.GET.copy()
    
    for key, value in kwargs.items():
        if value:
            query_dict[key] = value
        elif key in query_dict:
            del query_dict[key]
    
    if query_dict:
        return '?' + query_dict.urlencode()
    return ''


@register.filter
def get_item(dictionary, key):
    """
    Get item from dictionary by key.
    """
    return dictionary.get(key)


@register.simple_tag
def settings_value(name):
    """
    Get Django settings value.
    """
    from django.conf import settings
    return getattr(settings, name, None)
