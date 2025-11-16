"""
Test CMS models
"""
import pytest
from django.core.exceptions import ValidationError
from .factories import (
    HeroSlideFactory, ExpertCardFactory, FeaturedCourseFactory,
    PageSVGFactory, EventGridCellFactory, TrackingPixelFactory
)


@pytest.mark.django_db
class TestHeroSlide:
    """Test HeroSlide model"""
    
    def test_create_hero_slide(self):
        """Test basic creation"""
        slide = HeroSlideFactory()
        assert slide.id is not None
        assert slide.is_active is True
    
    def test_ordering(self):
        """Test slides are ordered correctly"""
        slide1 = HeroSlideFactory(order=1)
        slide2 = HeroSlideFactory(order=2)
        slide3 = HeroSlideFactory(order=3)
        
        from apps.cms.models import HeroSlide
        slides = list(HeroSlide.objects.all())
        
        assert slides[0].order == 1
        assert slides[1].order == 2
        assert slides[2].order == 3


@pytest.mark.django_db
class TestPageSVG:
    """Test PageSVG model"""
    
    def test_get_svg_ukraine_light(self):
        """Test getting Ukraine light SVG"""
        svg = PageSVGFactory()
        result = svg.get_svg('UA', 'light')
        assert '<svg>' in result
        assert 'E50914' in result  # Red color
    
    def test_get_svg_fallback_to_ukraine(self):
        """Test fallback to Ukraine when World version empty"""
        svg = PageSVGFactory(svg_world_light='', svg_world_dark='')
        result = svg.get_svg('US', 'light')
        # Should fallback to UA version
        assert 'E50914' in result


@pytest.mark.django_db
class TestEventGridCell:
    """Test EventGridCell model"""
    
    def test_position_unique(self):
        """Test positions are unique"""
        cell1 = EventGridCellFactory(position=1)
        
        with pytest.raises(Exception):  # IntegrityError wrapped by Django
            EventGridCellFactory(position=1)


@pytest.mark.django_db
class TestTrackingPixel:
    """Test TrackingPixel model"""
    
    def test_create_facebook_pixel(self):
        """Test Facebook pixel creation"""
        pixel = TrackingPixelFactory(
            pixel_type='facebook',
            pixel_id='123456789'
        )
        assert pixel.get_pixel_type_display() == 'Facebook Pixel'
    
    def test_unique_pixel_type_and_id(self):
        """Test pixel_type + pixel_id must be unique"""
        TrackingPixelFactory(pixel_type='facebook', pixel_id='123')
        
        with pytest.raises(Exception):
            TrackingPixelFactory(pixel_type='facebook', pixel_id='123')

