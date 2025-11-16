"""
Celery tasks for CMS
Cache warming and content optimization
"""
from celery import shared_task
from django.core.cache import cache
from apps.core.cache import CacheStrategy
import logging

logger = logging.getLogger(__name__)


@shared_task
def warm_all_caches():
    """
    Warm all CMS content caches (runs every 15 minutes)
    
    Pre-loads frequently accessed content into Redis cache.
    """
    try:
        from .models import HeroSlide, ExpertCard, FeaturedCourse
        
        warm_count = 0
        
        # Warm hero slides for both versions
        for country in ['UA', 'WORLD']:
            hero_slides = list(
                HeroSlide.objects.filter(is_active=True)
                .order_by('order')[:7]
                .values('id', 'title', 'subtitle', 'cta_text', 'order')
            )
            cache_key = f"hero_slides_{country}"
            cache.set(cache_key, hero_slides, CacheStrategy.TTL_LONG)
            warm_count += 1
        
        # Warm expert cards
        expert_cards = list(
            ExpertCard.objects.filter(is_active=True, show_on_homepage=True)
            .order_by('order')
            .values('id', 'name', 'position', 'specialization', 'bio', 'order')
        )
        cache.set('expert_cards_homepage', expert_cards, CacheStrategy.TTL_LONG)
        warm_count += 1
        
        # Warm featured courses
        featured_courses = list(
            FeaturedCourse.objects.filter(is_active=True, page='home')
            .select_related('course')
            .order_by('order')[:12]
            .values('id', 'course__title', 'course__slug', 'order')
        )
        cache.set('featured_courses_home', featured_courses, CacheStrategy.TTL_LONG)
        warm_count += 1
        
        logger.info(f"Warmed {warm_count} cache keys")
        return warm_count
        
    except Exception as e:
        logger.error(f"Failed to warm caches: {e}")
        return 0


@shared_task
def invalidate_hero_cache():
    """
    Invalidate hero slides cache when content changes
    
    Called after admin save/delete of HeroSlide.
    """
    try:
        CacheStrategy.invalidate_pattern('hero_slides_*')
        logger.info("Hero slides cache invalidated")
        return True
    except Exception as e:
        logger.error(f"Failed to invalidate hero cache: {e}")
        return False


@shared_task
def optimize_images():
    """
    Optimize uploaded images for web delivery
    
    Runs nightly to resize and compress images.
    """
    try:
        from .models import HeroSlide, ExpertCard
        from PIL import Image
        from io import BytesIO
        from django.core.files.uploadedfile import InMemoryUploadedFile
        
        optimized_count = 0
        
        # Optimize hero slides
        for slide in HeroSlide.objects.filter(is_active=True):
            if slide.image and hasattr(slide.image, 'path'):
                try:
                    img = Image.open(slide.image.path)
                    if img.height > 1080 or img.width > 1920:
                        # Needs optimization
                        logger.info(f"Optimizing hero slide #{slide.id}")
                        slide.save()  # Triggers auto-optimization
                        optimized_count += 1
                except Exception as e:
                    logger.warning(f"Failed to optimize slide #{slide.id}: {e}")
        
        logger.info(f"Optimized {optimized_count} images")
        return optimized_count
        
    except Exception as e:
        logger.error(f"Failed to optimize images: {e}")
        return 0

