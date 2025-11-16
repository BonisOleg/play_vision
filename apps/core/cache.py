"""
Caching strategy for Play Vision
Multi-tier caching with Redis backend
"""
from django.core.cache import cache
from django.conf import settings
from functools import wraps
import hashlib
import logging

logger = logging.getLogger(__name__)


class CacheStrategy:
    """
    Multi-tier caching with automatic invalidation
    
    Usage:
        @CacheStrategy.cached_query('my_key', ttl=CacheStrategy.TTL_LONG)
        def get_data():
            return expensive_query()
    """
    
    # Cache TTL constants
    TTL_SHORT = 60  # 1 minute
    TTL_MEDIUM = 300  # 5 minutes  
    TTL_LONG = 3600  # 1 hour
    TTL_DAY = 86400  # 24 hours
    TTL_WEEK = 604800  # 7 days
    
    @staticmethod
    def get_cache_key(prefix, *args, **kwargs):
        """
        Generate deterministic cache key from arguments
        
        Args:
            prefix: Cache key prefix (e.g. 'hero_slides')
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            str: MD5 hash of the key components
        """
        # Sort kwargs for consistency
        sorted_kwargs = sorted(kwargs.items())
        key_data = f"{prefix}:{args}:{sorted_kwargs}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    @classmethod
    def cached_query(cls, key_prefix, ttl=TTL_MEDIUM):
        """
        Decorator for caching queryset/function results
        
        Args:
            key_prefix: Prefix for cache key
            ttl: Time to live in seconds
        
        Example:
            @cached_query('active_courses', ttl=3600)
            def get_active_courses(category_id):
                return Course.objects.filter(category_id=category_id, is_active=True)
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = cls.get_cache_key(key_prefix, *args, **kwargs)
                
                # Try to get from cache
                result = cache.get(cache_key)
                
                if result is None:
                    # Cache miss - execute function
                    logger.debug(f"Cache MISS for key: {cache_key}")
                    result = func(*args, **kwargs)
                    
                    # Store in cache
                    cache.set(cache_key, result, ttl)
                    logger.debug(f"Cached result for key: {cache_key} (TTL: {ttl}s)")
                else:
                    logger.debug(f"Cache HIT for key: {cache_key}")
                
                return result
            
            return wrapper
        return decorator
    
    @classmethod
    def invalidate_pattern(cls, pattern):
        """
        Invalidate all cache keys matching a pattern
        
        Args:
            pattern: Wildcard pattern (e.g. 'hero_*', '*_slides_*')
        
        Note:
            Requires Redis backend with SCAN support
        """
        try:
            from django_redis import get_redis_connection
            
            conn = get_redis_connection("default")
            count = 0
            
            # Use SCAN to find matching keys
            for key in conn.scan_iter(match=f"*{pattern}*"):
                conn.delete(key)
                count += 1
            
            logger.info(f"Invalidated {count} cache keys matching '{pattern}'")
            return count
            
        except Exception as e:
            logger.error(f"Failed to invalidate cache pattern '{pattern}': {e}")
            return 0
    
    @classmethod
    def invalidate_key(cls, key_prefix, *args, **kwargs):
        """
        Invalidate specific cache key
        
        Args:
            key_prefix: Cache key prefix
            *args, **kwargs: Arguments used to generate key
        """
        cache_key = cls.get_cache_key(key_prefix, *args, **kwargs)
        cache.delete(cache_key)
        logger.debug(f"Invalidated cache key: {cache_key}")
    
    @classmethod
    def warm_cache(cls, key_prefix, func, *args, **kwargs):
        """
        Proactively warm cache by executing function
        
        Args:
            key_prefix: Cache key prefix
            func: Function to execute
            *args, **kwargs: Arguments to pass to function
        """
        try:
            cache_key = cls.get_cache_key(key_prefix, *args, **kwargs)
            result = func(*args, **kwargs)
            cache.set(cache_key, result, cls.TTL_LONG)
            logger.info(f"Warmed cache for key: {cache_key}")
            return result
        except Exception as e:
            logger.error(f"Failed to warm cache for '{key_prefix}': {e}")
            return None


def cache_page_for_user(ttl=300):
    """
    Cache entire page per user
    
    Args:
        ttl: Time to live in seconds
    
    Example:
        @cache_page_for_user(ttl=600)
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                # Don't cache for anonymous users
                return view_func(request, *args, **kwargs)
            
            # Generate cache key from user and path
            cache_key = CacheStrategy.get_cache_key(
                'page_cache',
                request.user.id,
                request.path,
                request.GET.urlencode()
            )
            
            # Try cache
            response = cache.get(cache_key)
            
            if response is None:
                # Execute view
                response = view_func(request, *args, **kwargs)
                # Cache response
                cache.set(cache_key, response, ttl)
            
            return response
        
        return wrapper
    return decorator

