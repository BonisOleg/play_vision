from django.utils import timezone
from .models import Event


def upcoming_events(request):
    """Context processor to provide upcoming events globally"""
    events = Event.objects.filter(
        status='published',
        start_datetime__gt=timezone.now()
    ).select_related('organizer').order_by('start_datetime')[:7]
    
    return {
        'upcoming_events_menu': events
    }
