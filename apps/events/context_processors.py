from django.utils import timezone
from django.db import connection
from .models import Event


def event_categories_menu(request):
    """Static categories menu for events"""
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
            return {'event_categories_menu': []}
        
        categories = []
        for cat_value, cat_display in Event.EVENT_CATEGORY_CHOICES:
            try:
                # Підрахунок майбутніх подій категорії
                count = Event.objects.filter(
                    status='published',
                    event_category=cat_value,
                    start_datetime__gt=timezone.now()
                ).count()
                
                if count > 0:  # Показуємо тільки категорії з подіями
                    categories.append({
                        'slug': cat_value,
                        'name': cat_display,
                        'count': count,
                        'url': f'/events/?category={cat_value}'
                    })
            except Exception as e:
                continue
        
        return {'event_categories_menu': categories}
    except Exception as e:
        # If any database error occurs, return empty categories list
        return {
            'event_categories_menu': []
        }
