"""
CMS context processors
Add tracking pixels and CMS data to all templates
"""
from django.core.cache import cache
from apps.core.cache import CacheStrategy


def tracking_pixels(request):
    """
    Add active tracking pixels to context
    
    Usage in base template:
        {% for pixel in tracking_pixels_head %}
            {{ pixel.code_snippet|safe }}
        {% endfor %}
    """
    from .models import TrackingPixel
    
    # Cache pixels for 1 hour
    cache_key = 'tracking_pixels_active'
    pixels = cache.get(cache_key)
    
    if pixels is None:
        pixels = {
            'head': list(
                TrackingPixel.objects.filter(is_active=True, placement='head')
                .values('pixel_type', 'code_snippet')
            ),
            'body_start': list(
                TrackingPixel.objects.filter(is_active=True, placement='body_start')
                .values('pixel_type', 'code_snippet')
            ),
            'body_end': list(
                TrackingPixel.objects.filter(is_active=True, placement='body_end')
                .values('pixel_type', 'code_snippet')
            ),
        }
        cache.set(cache_key, pixels, CacheStrategy.TTL_LONG)
    
    return {
        'tracking_pixels_head': pixels['head'],
        'tracking_pixels_body_start': pixels['body_start'],
        'tracking_pixels_body_end': pixels['body_end'],
    }


def featured_content(request):
    """
    Add featured content to context
    
    Optimized with caching and select_related.
    """
    from .models import HeroSlide, ExpertCard, FeaturedCourse
    
    # Get country from request (set by middleware)
    country = getattr(request, 'country_code', 'UA')
    
    # Hero slides (cached)
    cache_key = f'hero_slides_{country}'
    hero_slides = cache.get(cache_key)
    
    if hero_slides is None:
        hero_slides = list(
            HeroSlide.objects.filter(is_active=True)
            .order_by('order')[:7]
        )
        cache.set(cache_key, hero_slides, CacheStrategy.TTL_LONG)
    
    # Expert cards for team carousel (cached)
    cache_key = 'expert_cards_active'
    expert_cards = cache.get(cache_key)
    
    if expert_cards is None:
        expert_cards = list(
            ExpertCard.objects.filter(is_active=True, show_on_homepage=True)
            .order_by('order')
        )
        cache.set(cache_key, expert_cards, CacheStrategy.TTL_LONG)
    
    return {
        'hero_slides': hero_slides,
        'expert_cards': expert_cards,
        'expert_cards_count': len(expert_cards),
        'show_carousel_arrows': len(expert_cards) > 4,
    }

