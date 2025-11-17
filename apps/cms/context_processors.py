"""
Context processor для визначення країни та теми
"""
import geoip2.database
from django.conf import settings
import os


def get_client_ip(request):
    """Отримати IP користувача"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_country_code(request):
    """Визначити країну по IP"""
    try:
        ip = get_client_ip(request)
        
        # Локальні IP = UA
        if ip in ['127.0.0.1', 'localhost'] or ip.startswith('192.168.'):
            return 'UA'
        
        # GeoIP lookup
        geoip_path = os.path.join(settings.BASE_DIR, 'geoip', 'GeoLite2-Country.mmdb')
        if os.path.exists(geoip_path):
            with geoip2.database.Reader(geoip_path) as reader:
                response = reader.country(ip)
                return response.country.iso_code
        
        return 'UA'  # Fallback
    except Exception:
        return 'UA'  # Fallback при будь-якій помилці


def site_content(request):
    """
    Додає country_code та theme в контекст для всіх templates
    """
    # Визначити країну
    country_code = get_country_code(request)
    
    # Визначити тему (з cookies або session)
    theme = request.COOKIES.get('theme', 'light')
    if theme not in ['light', 'dark']:
        theme = 'light'
    
    return {
        'country_code': country_code,
        'theme': theme,
        'is_ukraine': country_code == 'UA',
    }
