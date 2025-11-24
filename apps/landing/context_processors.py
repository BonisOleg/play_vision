from django.conf import settings


def analytics(request):
    """
    Context processor для додавання analytics IDs в шаблони
    """
    return {
        'GOOGLE_ANALYTICS_ID': getattr(settings, 'GOOGLE_ANALYTICS_ID', ''),
        'FACEBOOK_PIXEL_ID': getattr(settings, 'FACEBOOK_PIXEL_ID', ''),
    }

