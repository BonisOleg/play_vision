from django.utils import timezone
from django.db import connection
from .models import Event


def upcoming_events(request):
    """Context processor to provide upcoming events globally"""
    try:
        # Check if events table exists before querying
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'events'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
        if not table_exists:
            return {'upcoming_events_menu': []}
            
        events = Event.objects.filter(
            status='published',
            start_datetime__gt=timezone.now()
        ).select_related('organizer').order_by('start_datetime')[:7]
        
        return {
            'upcoming_events_menu': events
        }
    except Exception as e:
        # If any database error occurs, return empty events list
        return {
            'upcoming_events_menu': []
        }
