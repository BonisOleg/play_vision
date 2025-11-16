"""
Core services for Play Vision
Geolocation, profiling, and other utilities
"""
import geoip2.database
import geoip2.errors
from django.conf import settings
from django.core.cache import cache
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)


class GeolocationService:
    """
    Production-ready IP geolocation with fallback and caching
    
    Usage:
        country = GeolocationService.get_country_from_ip('8.8.8.8')
        # Returns: 'US'
    """
    
    _reader = None  # Singleton pattern
    
    @classmethod
    def get_reader(cls):
        """
        Lazy load GeoIP2 database reader (singleton)
        
        Returns:
            geoip2.database.Reader or None
        """
        if cls._reader is None:
            try:
                geoip_path = settings.GEOIP_PATH
                db_file = geoip_path / 'GeoLite2-Country.mmdb'
                
                if not db_file.exists():
                    logger.warning(
                        f"GeoIP database not found at {db_file}. "
                        "Download from https://dev.maxmind.com/geoip/geolite2-free-geolocation-data"
                    )
                    return None
                
                cls._reader = geoip2.database.Reader(str(db_file))
                logger.info("GeoIP database loaded successfully")
                
            except Exception as e:
                logger.error(f"Failed to load GeoIP database: {e}")
                cls._reader = None
        
        return cls._reader
    
    @classmethod
    def get_country_from_ip(cls, ip_address):
        """
        Get country code from IP address with caching and fallback
        
        Args:
            ip_address: IPv4 or IPv6 address string
        
        Returns:
            str: 2-letter ISO country code (e.g. 'UA', 'US') or 'WORLD' if unknown
        """
        # Check cache first (24h TTL)
        cache_key = f"geoip:{ip_address}"
        cached_country = cache.get(cache_key)
        
        if cached_country:
            logger.debug(f"GeoIP cache HIT for {ip_address}: {cached_country}")
            return cached_country
        
        # Check if private/local IP
        if cls._is_private_ip(ip_address):
            logger.debug(f"Private IP detected: {ip_address}, returning UA")
            return 'UA'  # Default for localhost/private networks
        
        try:
            reader = cls.get_reader()
            
            if reader is None:
                logger.warning("GeoIP reader not available, using fallback")
                return 'WORLD'
            
            # Lookup country
            response = reader.country(ip_address)
            country_code = response.country.iso_code
            
            if not country_code:
                logger.warning(f"No country code for IP {ip_address}")
                return 'WORLD'
            
            # Cache for 24 hours
            cache.set(cache_key, country_code, 86400)
            logger.info(f"IP {ip_address} resolved to {country_code}")
            
            return country_code
            
        except geoip2.errors.AddressNotFoundError:
            logger.warning(f"IP {ip_address} not found in GeoIP database")
            cache.set(cache_key, 'WORLD', 86400)
            return 'WORLD'
            
        except Exception as e:
            logger.error(f"GeoIP lookup failed for {ip_address}: {e}")
            return 'WORLD'
    
    @staticmethod
    def _is_private_ip(ip):
        """
        Check if IP address is private/local
        
        Args:
            ip: IP address string
        
        Returns:
            bool: True if private, False otherwise
        """
        try:
            import ipaddress
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private or ip_obj.is_loopback
        except ValueError:
            logger.warning(f"Invalid IP address: {ip}")
            return False
    
    @classmethod
    def close(cls):
        """Close GeoIP reader (call on shutdown)"""
        if cls._reader:
            cls._reader.close()
            cls._reader = None


def profile_query(threshold_ms=100):
    """
    Decorator to log slow queries/functions
    
    Args:
        threshold_ms: Threshold in milliseconds to log warning
    
    Usage:
        @profile_query(threshold_ms=200)
        def expensive_function():
            # ... slow code ...
    """
    performance_logger = logging.getLogger('performance')
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.time() - start_time) * 1000
                
                if duration_ms > threshold_ms:
                    performance_logger.warning(
                        f"Slow operation in {func.__name__}: {duration_ms:.2f}ms "
                        f"(threshold: {threshold_ms}ms)"
                    )
                else:
                    performance_logger.debug(
                        f"{func.__name__} completed in {duration_ms:.2f}ms"
                    )
        
        return wrapper
    return decorator


class RequestContextMiddleware:
    """
    Store current request in thread-local storage for access in signals/tasks
    
    Add to MIDDLEWARE in settings.py
    """
    
    _thread_locals = None
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Initialize thread-local storage
        import threading
        RequestContextMiddleware._thread_locals = threading.local()
    
    def __call__(self, request):
        # Store request in thread-local
        RequestContextMiddleware._thread_locals.request = request
        
        try:
            response = self.get_response(request)
            return response
        finally:
            # Clean up
            if hasattr(RequestContextMiddleware._thread_locals, 'request'):
                del RequestContextMiddleware._thread_locals.request
    
    @classmethod
    def get_current_request(cls):
        """
        Get current request from thread-local storage
        
        Returns:
            HttpRequest or None
        """
        if cls._thread_locals is None:
            return None
        
        return getattr(cls._thread_locals, 'request', None)


# Helper function for easy access
def get_current_request():
    """Get current HTTP request from thread-local storage"""
    return RequestContextMiddleware.get_current_request()


def get_client_ip(request):
    """
    Get real client IP address handling proxies
    
    Args:
        request: Django HttpRequest object
    
    Returns:
        str: Client IP address
    """
    # Render.com uses X-Forwarded-For
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # First IP in chain is the real client
        ip = x_forwarded_for.split(',')[0].strip()
        return ip
    
    # CloudFlare uses CF-Connecting-IP
    cf_ip = request.META.get('HTTP_CF_CONNECTING_IP')
    if cf_ip:
        return cf_ip
    
    # Fallback to REMOTE_ADDR
    return request.META.get('REMOTE_ADDR', '127.0.0.1')

