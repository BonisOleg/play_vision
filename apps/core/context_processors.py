"""
Context processors для глобальних даних в templates
"""


def external_urls(request):
    """Глобальні зовнішні URL для використання в templates"""
    from django.conf import settings
    try:
        from apps.cms.models import SiteSettings
        site_settings = SiteSettings.get_settings()
        return {
            'external_auth_url': site_settings.external_auth_url,
            'external_join_url_default': site_settings.external_join_url_default,
            'BUNNY_LIBRARY_ID': settings.BUNNY_LIBRARY_ID,
        }
    except Exception:
        # Fallback якщо модель недоступна
        return {
            'external_auth_url': '#',
            'external_join_url_default': '#',
            'BUNNY_LIBRARY_ID': getattr(settings, 'BUNNY_LIBRARY_ID', ''),
        }

