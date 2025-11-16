"""
Factory Boy factories for CMS models
"""
import factory
from factory.django import DjangoModelFactory
from apps.cms.models import (
    HeroSlide, ExpertCard, FeaturedCourse,
    PageSVG, EventGridCell, TrackingPixel
)


class HeroSlideFactory(DjangoModelFactory):
    """Factory for HeroSlide"""
    class Meta:
        model = HeroSlide
    
    title = factory.Sequence(lambda n: f"Hero Slide {n}")
    subtitle = factory.Faker('sentence', nb_words=8)
    badge = factory.Faker('word')
    cta_text = "Learn More"
    cta_url = "/hub/"
    order = factory.Sequence(lambda n: (n % 7) + 1)
    is_active = True


class ExpertCardFactory(DjangoModelFactory):
    """Factory for ExpertCard"""
    class Meta:
        model = ExpertCard
    
    name = factory.Faker('name')
    position = factory.Faker('job')
    specialization = factory.Faker('sentence', nb_words=4)
    bio = factory.Faker('text', max_nb_chars=200)
    order = factory.Sequence(lambda n: n)
    is_active = True
    show_on_homepage = True


class FeaturedCourseFactory(DjangoModelFactory):
    """Factory for FeaturedCourse"""
    class Meta:
        model = FeaturedCourse
    
    page = 'home'
    order = factory.Sequence(lambda n: (n % 12) + 1)
    is_active = True


class PageSVGFactory(DjangoModelFactory):
    """Factory for PageSVG"""
    class Meta:
        model = PageSVG
    
    name = factory.Sequence(lambda n: f"svg_{n}")
    page = 'home'
    section = 'section1'
    svg_ua_light = '<svg><circle cx="50" cy="50" r="40" fill="#E50914"/></svg>'
    svg_ua_dark = '<svg><circle cx="50" cy="50" r="40" fill="#ffffff"/></svg>'
    is_active = True


class EventGridCellFactory(DjangoModelFactory):
    """Factory for EventGridCell"""
    class Meta:
        model = EventGridCell
    
    position = factory.Sequence(lambda n: (n % 9) + 1)
    alt_text = factory.Faker('sentence', nb_words=3)
    is_active = True


class TrackingPixelFactory(DjangoModelFactory):
    """Factory for TrackingPixel"""
    class Meta:
        model = TrackingPixel
    
    name = factory.Sequence(lambda n: f"Pixel {n}")
    pixel_type = 'facebook'
    pixel_id = factory.Sequence(lambda n: f"FB-{n}")
    code_snippet = '<!-- Facebook Pixel Code -->'
    placement = 'head'
    is_active = True

