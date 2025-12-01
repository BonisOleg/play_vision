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
    Додає country_code, theme та CMS контент в контекст всіх templates
    """
    # Визначити країну та тему
    country_code = get_country_code(request)
    theme = request.COOKIES.get('theme', 'light')
    if theme not in ['light', 'dark']:
        theme = 'light'
    
    # Імпортувати CMS моделі
    from apps.cms.models import HeroSlide, ExpertCard, FeaturedCourse
    from django.core.cache import cache
    
    # Hero Slides - кеш 5 хв
    hero_slides = cache.get('cms_hero_slides')
    if hero_slides is None:
        hero_slides = list(
            HeroSlide.objects.filter(is_active=True).order_by('order')
        )
        cache.set('cms_hero_slides', hero_slides, 60*5)
    
    # Expert Cards - окремо для кожної сторінки (кеш 10 хв)
    experts_home = cache.get('cms_experts_home')
    if experts_home is None:
        experts_home = list(
            ExpertCard.objects.filter(is_active=True, show_on_home=True).order_by('order_home')
        )
        cache.set('cms_experts_home', experts_home, 60*10)
    
    experts_about = cache.get('cms_experts_about')
    if experts_about is None:
        experts_about = list(
            ExpertCard.objects.filter(is_active=True, show_on_about=True).order_by('order_about')
        )
        cache.set('cms_experts_about', experts_about, 60*10)
    
    experts_mentoring = cache.get('cms_experts_mentoring')
    if experts_mentoring is None:
        experts_mentoring = list(
            ExpertCard.objects.filter(is_active=True, show_on_mentoring=True).order_by('order_mentoring')
        )
        cache.set('cms_experts_mentoring', experts_mentoring, 60*10)
    
    # Backward compatibility
    experts = experts_home
    
    # Featured Courses - кеш 5 хв
    main_courses = cache.get('cms_main_courses')
    if main_courses is None:
        featured = FeaturedCourse.objects.filter(
            is_active=True,
            page='home'
        ).select_related('course').order_by('order')
        main_courses = [
            f.course for f in featured 
            if f.course and f.course.is_published
        ]
        cache.set('cms_main_courses', main_courses, 60*5)
    
    return {
        'country_code': country_code,
        'theme': theme,
        'is_ukraine': country_code == 'UA',
        # CMS дані (можуть бути порожні списки якщо немає в БД):
        'cms_hero_slides': hero_slides,
        'cms_experts': experts,  # Backward compatibility
        'cms_experts_home': experts_home,
        'cms_experts_about': experts_about,
        'cms_experts_mentoring': experts_mentoring,
        'main_courses': main_courses,
    }
