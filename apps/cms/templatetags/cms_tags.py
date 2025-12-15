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


@register.filter
def get_item(lst, index):
    """Отримати елемент за індексом з лісту"""
    try:
        return lst[index] if isinstance(lst, (list, tuple)) else None
    except (IndexError, TypeError):
        return None


@register.filter
def getattr(obj, attr_name):
    """Отримати атрибут об'єкта за назвою"""
    try:
        return getattr(obj, attr_name, None)
    except Exception:
        return None


@register.simple_tag
def get_svg_light_by_index(section, index, country_code='UA', theme='light'):
    """Отримати SVG light за індексом (1-6) для секції 4"""
    try:
        if not section:
            return ''
        
        # Формуємо назву поля
        field_light = f"svg_{index}_{'ua' if country_code == 'UA' else 'world'}_{theme}"
        svg_light = getattr(section, field_light, '')
        
        # Fallback: World → UA
        if not svg_light and country_code != 'UA':
            svg_light = getattr(section, f"svg_{index}_ua_{theme}", '')
        
        return svg_light or ''
    except Exception:
        return ''


@register.simple_tag
def get_svg_dark_by_index(section, index, country_code='UA', theme='light'):
    """Отримати SVG dark за індексом (1-6) для секції 4"""
    try:
        if not section:
            return ''
        
        # Формуємо назву поля
        field_dark = f"svg_{index}_{'ua' if country_code == 'UA' else 'world'}_dark"
        svg_dark = getattr(section, field_dark, '')
        
        # Fallback: World → UA
        if not svg_dark and country_code != 'UA':
            svg_dark = getattr(section, f"svg_{index}_ua_dark", '')
        
        # Fallback: Dark → Light (використовуємо той самий логічний підхід)
        if not svg_dark:
            field_light = f"svg_{index}_{'ua' if country_code == 'UA' else 'world'}_{theme}"
            svg_dark = getattr(section, field_light, '')
            if not svg_dark and country_code != 'UA':
                svg_dark = getattr(section, f"svg_{index}_ua_{theme}", '')
        
        return svg_dark or ''
    except Exception:
        return ''


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
def get_about_section3_svg_list(country_code='UA', theme='light'):
    """Отримати список 3 SVG для grid Секції 3"""
    try:
        section = AboutSection3.objects.filter(is_active=True).first()
        if section:
            return section.get_svg_list(country_code, theme)
        return []
    except Exception:
        return []


@register.simple_tag
def get_about_section4_svg_list(country_code='UA', theme='light'):
    """Отримати список 6 SVG для grid Секції 4"""
    try:
        section = AboutSection4.objects.filter(is_active=True).first()
        if section:
            return section.get_svg_list(country_code, theme)
        return []
    except Exception:
        return []


@register.simple_tag
def get_hub_hero():
    """Отримати Hero для Хаб знань"""
    try:
        return HubHero.objects.filter(is_active=True).first()
    except HubHero.DoesNotExist:
        return None


@register.filter
def get_background_image(hub_hero, number):
    """Отримати бекграунд зображення для слайда"""
    if not hub_hero:
        return None
    try:
        num = int(number)
        image = hub_hero.get_background_image(num)
        return image
    except (ValueError, AttributeError, TypeError):
        return None


@register.filter
def get_background_video(hub_hero, number):
    """Отримати бекграунд відео для слайда"""
    if not hub_hero:
        return None
    try:
        num = int(number)
        video = hub_hero.get_background_video(num)
        return video
    except (ValueError, AttributeError, TypeError):
        return None


@register.simple_tag
def get_hub_hero_title(hub_hero, number, country_code='UA'):
    """Отримати заголовок для слайда HubHero"""
    if not hub_hero:
        return ''
    try:
        num = int(number)
        return hub_hero.get_title(num, country_code)
    except (ValueError, AttributeError, TypeError):
        return ''


@register.simple_tag
def get_hub_hero_subtitle(hub_hero, number, country_code='UA'):
    """Отримати підзаголовок для слайда HubHero"""
    if not hub_hero:
        return ''
    try:
        num = int(number)
        return hub_hero.get_subtitle(num, country_code)
    except (ValueError, AttributeError, TypeError):
        return ''


@register.filter
def get_title(hub_hero, number):
    """Отримати заголовок для слайда HubHero (filter для зворотної сумісності)"""
    if not hub_hero:
        return ''
    try:
        num = int(number)
        # За замовчуванням UA, але метод має fallback
        return hub_hero.get_title(num, 'UA')
    except (ValueError, AttributeError, TypeError):
        return ''


@register.filter
def get_subtitle(hub_hero, number):
    """Отримати підзаголовок для слайда HubHero (filter для зворотної сумісності)"""
    if not hub_hero:
        return ''
    try:
        num = int(number)
        return hub_hero.get_subtitle(num, 'UA')
    except (ValueError, AttributeError, TypeError):
        return ''


@register.simple_tag
def get_hub_hero_cta_text(hub_hero, number, country_code='UA'):
    """Отримати CTA текст для слайда HubHero"""
    if not hub_hero:
        return ''
    try:
        num = int(number)
        return hub_hero.get_cta_text(num, country_code)
    except (ValueError, AttributeError, TypeError):
        return ''


@register.simple_tag
def get_hub_hero_cta_url(hub_hero, number):
    """Отримати CTA URL для слайда HubHero"""
    if not hub_hero:
        return '#catalog'
    try:
        num = int(number)
        return hub_hero.get_cta_url(num) or '#catalog'
    except (ValueError, AttributeError, TypeError):
        return '#catalog'


@register.filter
def get_cta_text(hub_hero, number):
    """Отримати CTA текст для слайда HubHero (filter для зворотної сумісності)"""
    if not hub_hero:
        return ''
    try:
        num = int(number)
        return hub_hero.get_cta_text(num, 'UA')
    except (ValueError, AttributeError, TypeError):
        return ''


@register.filter
def get_cta_url(hub_hero, number):
    """Отримати CTA URL для слайда HubHero (filter для зворотної сумісності)"""
    if not hub_hero:
        return '#catalog'
    try:
        num = int(number)
        return hub_hero.get_cta_url(num) or '#catalog'
    except (ValueError, AttributeError, TypeError):
        return '#catalog'


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
def highlight_second_word(text):
    """Обгортає друге слово в span з класом text-highlight"""
    if not text:
        return ''
    words = text.split()
    if len(words) < 2:
        return text
    words[1] = f'<span class="text-highlight">{words[1]}</span>'
    return ' '.join(words)


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


@register.filter
def get_video_library_id(obj, country_code):
    """Отримати Library ID для відео"""
    if not obj:
        return ''
    if hasattr(obj, 'get_video_library_id'):
        return obj.get_video_library_id(country_code)
    return ''


@register.filter
def get_video_id(obj, country_code):
    """Отримати Video ID для відео"""
    if not obj:
        return ''
    if hasattr(obj, 'get_video_id'):
        return obj.get_video_id(country_code)
    return ''


@register.filter
def has_video(obj, country_code):
    """Перевірити чи є відео"""
    if not obj:
        return False
    if hasattr(obj, 'has_video'):
        return obj.has_video(country_code)
    return False

