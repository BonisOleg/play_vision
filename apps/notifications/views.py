from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification, NotificationPreference


@login_required
def notification_list(request):
    """
    Сторінка зі списком сповіщень користувача
    """
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:50]
    
    context = {
        'notifications': notifications,
        'unread_count': notifications.filter(status='sent').count(),
    }
    
    return render(request, 'notifications/list.html', context)


@login_required  
def notification_preferences(request):
    """
    Налаштування сповіщень користувача
    """
    preferences, created = NotificationPreference.objects.get_or_create(
        user=request.user
    )
    
    if request.method == 'POST':
        # Оновлюємо налаштування
        preferences.email_enabled = request.POST.get('email_enabled') == 'on'
        preferences.push_enabled = request.POST.get('push_enabled') == 'on'
        preferences.marketing_emails = request.POST.get('marketing_emails') == 'on'
        preferences.course_updates = request.POST.get('course_updates') == 'on'
        preferences.event_reminders = request.POST.get('event_reminders') == 'on'
        preferences.save()
        
        return JsonResponse({'success': True})
    
    context = {
        'preferences': preferences,
    }
    
    return render(request, 'notifications/preferences.html', context)
