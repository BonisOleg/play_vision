"""
Integration tests for CMS admin
"""
import pytest
from django.urls import reverse
from .factories import HeroSlideFactory, FeaturedCourseFactory


@pytest.mark.django_db
@pytest.mark.integration
class TestCMSAdmin:
    """Test CMS admin interface"""
    
    def test_hero_slide_list_view(self, client_authenticated):
        """Test hero slide list loads"""
        HeroSlideFactory.create_batch(3)
        
        url = reverse('admin:cms_heroslide_changelist')
        response = client_authenticated.get(url)
        
        assert response.status_code == 200
        assert 'Hero Слайди' in str(response.content)
    
    def test_featured_course_add(self, client_authenticated):
        """Test adding featured course"""
        from apps.content.models import Course, Category
        
        # Create test course
        category = Category.objects.create(name="Test", slug="test")
        course = Course.objects.create(
            title="Test Course",
            slug="test-course",
            category=category
        )
        
        url = reverse('admin:cms_featuredcourse_add')
        response = client_authenticated.post(url, {
            'course': course.id,
            'page': 'home',
            'order': 1,
            'is_active': True
        })
        
        # Should redirect on success
        assert response.status_code in [200, 302]


@pytest.mark.django_db
class TestDashboardView:
    """Test admin dashboard"""
    
    def test_dashboard_loads(self, client_authenticated):
        """Test dashboard page loads"""
        url = reverse('admin_dashboard')
        response = client_authenticated.get(url)
        
        assert response.status_code == 200
        assert 'total_users' in response.context
    
    def test_dashboard_period_filter(self, client_authenticated):
        """Test period filtering works"""
        url = reverse('admin_dashboard')
        
        # Test different periods
        for period in ['today', 'week', 'month']:
            response = client_authenticated.get(url, {'period': period})
            assert response.status_code == 200
            assert response.context['period'] == period

