"""
Test core services - GeolocationService, CacheStrategy
"""
import pytest
from apps.core.services import GeolocationService
from apps.core.cache import CacheStrategy


@pytest.mark.unit
class TestGeolocationService:
    """Test IP geolocation"""
    
    def test_private_ip_returns_ua(self):
        """Test private IPs default to UA"""
        country = GeolocationService.get_country_from_ip('127.0.0.1')
        assert country == 'UA'
        
        country = GeolocationService.get_country_from_ip('192.168.1.1')
        assert country == 'UA'
    
    def test_is_private_ip(self):
        """Test private IP detection"""
        assert GeolocationService._is_private_ip('127.0.0.1') is True
        assert GeolocationService._is_private_ip('192.168.1.1') is True
        assert GeolocationService._is_private_ip('10.0.0.1') is True
        assert GeolocationService._is_private_ip('8.8.8.8') is False


@pytest.mark.unit
class TestCacheStrategy:
    """Test caching utilities"""
    
    def test_get_cache_key(self):
        """Test cache key generation"""
        key1 = CacheStrategy.get_cache_key('test', 1, 2, foo='bar')
        key2 = CacheStrategy.get_cache_key('test', 1, 2, foo='bar')
        
        # Same args should produce same key
        assert key1 == key2
    
    def test_cached_query_decorator(self):
        """Test cached query decorator"""
        call_count = 0
        
        @CacheStrategy.cached_query('test_query', ttl=60)
        def expensive_query(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call
        result1 = expensive_query(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call - should use cache
        result2 = expensive_query(5)
        assert result2 == 10
        assert call_count == 1  # Not incremented - used cache

