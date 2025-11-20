"""
Template tags для CMS контенту
"""
from django import template
from apps.cms.models import (
    HeroSlide, FeaturedCourse, ExpertCard, EventGridCell,
    AboutHero, AboutSection2, AboutSection3, AboutSection4,
    HubHero, MentorHero, MentorSection1Image, MentorSection2, 
    MentorSection3, MentorSection4, MentorCoachingSVG, TrackingPixel
)

register = template.Library()


@register.simple_tag
def get_hero_slides():
    """Отримати активні Hero слайди"""
    return HeroSlide.objects.filter(is_active=True).order_by('order')


@register.simple_tag
def get_featured_courses():
    """Отримати обрані курси для головної"""
    featured = FeaturedCourse.objects.filter(is_active=True).order_by('order')
    return [f.course for f in featured if f.course]


@register.simple_tag
def get_expert_cards():
    """Отримати картки команди"""
    return ExpertCard.objects.filter(is_active=True).order_by('order')


@register.simple_tag
def get_event_grid():
    """Отримати 9 комірок Event Grid"""
    return EventGridCell.objects.filter(is_active=True).order_by('position')[:9]


@register.simple_tag
def get_about_hero():
    """Отримати Hero для Про нас"""
    try:
        return AboutHero.objects.filter(is_active=True).first()
    except AboutHero.DoesNotExist:
        return None


@register.simple_tag
def get_about_section2():
    """Отримати Секцію 2 для Про нас"""
    try:
        return AboutSection2.objects.filter(is_active=True).first()
    except AboutSection2.DoesNotExist:
        return None


@register.simple_tag
def get_about_section3():
    """Отримати Секцію 3 для Про нас"""
    try:
        return AboutSection3.objects.filter(is_active=True).first()
    except AboutSection3.DoesNotExist:
        return None


@register.simple_tag
def get_about_section4():
    """Отримати Секцію 4 для Про нас"""
    try:
        return AboutSection4.objects.filter(is_active=True).first()
    except AboutSection4.DoesNotExist:
        return None


@register.simple_tag
def get_hub_hero():
    """Отримати Hero для Хаб знань"""
    try:
        return HubHero.objects.filter(is_active=True).first()
    except HubHero.DoesNotExist:
        return None


@register.simple_tag
def get_mentor_hero():
    """Отримати Hero для Ментор коучинг"""
    try:
        return MentorHero.objects.filter(is_active=True).first()
    except MentorHero.DoesNotExist:
        return None


@register.simple_tag
def get_mentor_section1_images():
    """Отримати 3 картинки Секції 1"""
    return MentorSection1Image.objects.filter(is_active=True).order_by('position')[:3]


@register.simple_tag
def get_mentor_section2():
    """Отримати Секцію 2 для Ментор"""
    try:
        return MentorSection2.objects.filter(is_active=True).first()
    except MentorSection2.DoesNotExist:
        return None


@register.simple_tag
def get_mentor_section3():
    """Отримати Секцію 3 для Ментор"""
    try:
        return MentorSection3.objects.filter(is_active=True).first()
    except MentorSection3.DoesNotExist:
        return None


@register.simple_tag
def get_mentor_section4():
    """Отримати Секцію 4 для Ментор"""
    try:
        return MentorSection4.objects.filter(is_active=True).first()
    except MentorSection4.DoesNotExist:
        return None


@register.simple_tag
def get_mentor_coaching_svg():
    """Отримати SVG для Ментор коучинг на Головній"""
    try:
        return MentorCoachingSVG.objects.filter(is_active=True).first()
    except MentorCoachingSVG.DoesNotExist:
        return None


@register.simple_tag
def get_tracking_pixels():
    """Отримати активні tracking pixels"""
    return TrackingPixel.objects.filter(is_active=True)


@register.filter
def for_country(obj, country_code):
    """
    Фільтр для отримання контенту по країні
    Usage: {{ hero_slide|for_country:country_code }}
    """
    if not obj:
        return obj
    
    # Якщо об'єкт має метод get_title/get_subtitle/etc
    if hasattr(obj, 'get_title'):
        return obj
    
    return obj


# Локалізаційні фільтри для CMS моделей
@register.filter
def get_localized_title(obj, country_code):
    """
    Отримати title з урахуванням країни користувача
    Використання: {{ slide|get_localized_title:country_code }}
    """
    if not obj:
        return ''
    if hasattr(obj, 'get_title'):
        return obj.get_title(country_code)
    # Fallback до прямих полів
    return getattr(obj, 'title_ua', getattr(obj, 'title', ''))


@register.filter
def get_localized_subtitle(obj, country_code):
    """
    Отримати subtitle з урахуванням країни
    Використання: {{ slide|get_localized_subtitle:country_code }}
    """
    if not obj:
        return ''
    if hasattr(obj, 'get_subtitle'):
        return obj.get_subtitle(country_code)
    return getattr(obj, 'subtitle_ua', getattr(obj, 'subtitle', ''))


@register.filter
def get_localized_cta_text(obj, country_code):
    """
    Отримати CTA button text з урахуванням країни
    Використання: {{ slide|get_localized_cta_text:country_code }}
    """
    if not obj:
        return ''
    if hasattr(obj, 'get_cta_text'):
        return obj.get_cta_text(country_code)
    return getattr(obj, 'cta_text_ua', getattr(obj, 'cta_text', ''))


@register.filter
def get_localized_image(obj, country_code):
    """
    Отримати image з урахуванням країни
    Використання: {{ hero|get_localized_image:country_code }}
    """
    if not obj:
        return None
    if hasattr(obj, 'get_image'):
        return obj.get_image(country_code)
    # Fallback до прямих полів
    return getattr(obj, 'image_ua', getattr(obj, 'image', None))


@register.simple_tag
def get_localized_svg(obj, country_code, theme='light'):
    """
    Отримати SVG контент з урахуванням країни і теми
    Використання: {% get_localized_svg section country_code theme %}
    """
    if not obj:
        return ''
    if hasattr(obj, 'get_svg'):
        return obj.get_svg(country_code, theme)
    # Fallback
    svg_field = f'svg_{country_code.lower()}_{theme}'
    return getattr(obj, svg_field, '')

