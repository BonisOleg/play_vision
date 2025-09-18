"""
Custom middleware for Play Vision project
"""
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
import time


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to all responses"""
    
    def process_response(self, request, response):
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response


class NoCacheMiddleware(MiddlewareMixin):
    """Disable caching in development mode to prevent template issues"""
    
    def process_response(self, request, response):
        from django.conf import settings
        
        # Only apply in DEBUG mode
        if settings.DEBUG:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            response['Last-Modified'] = ''
            response['ETag'] = ''
        
        return response


class BasicRateLimitMiddleware(MiddlewareMixin):
    """Basic rate limiting middleware"""
    
    def process_request(self, request):
        # Skip rate limiting for authenticated superusers
        if request.user.is_authenticated and request.user.is_superuser:
            return None
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Rate limit sensitive endpoints
        sensitive_paths = ['/auth/login/', '/auth/register/', '/auth/password-reset/']
        
        for path in sensitive_paths:
            if request.path.startswith(path):
                cache_key = f"rate_limit:{ip}:{path}"
                requests = cache.get(cache_key, 0)
                
                if requests >= 5:  # Max 5 requests per minute
                    return HttpResponse(
                        'Rate limit exceeded. Please try again later.',
                        status=429,
                        content_type='text/plain'
                    )
                
                cache.set(cache_key, requests + 1, 60)  # 1 minute window
        
        return None


class PaywallMiddleware(MiddlewareMixin):
    """Middleware to check content access"""
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Check if this is a course detail view
        if hasattr(view_func, 'view_class'):
            view_class = view_func.view_class
            
            # Add access check for course content
            if hasattr(view_class, 'model'):
                from apps.content.models import Course, Material
                
                if view_class.model == Course:
                    # Set flag for course access check
                    request.is_course_view = True
                elif view_class.model == Material:
                    # Set flag for material access check  
                    request.is_material_view = True
        
        return None


class MaintenanceMiddleware(MiddlewareMixin):
    """Maintenance mode middleware"""
    
    def process_request(self, request):
        from django.conf import settings
        
        # Check if maintenance mode is enabled
        maintenance_mode = getattr(settings, 'MAINTENANCE_MODE', False)
        
        if maintenance_mode:
            # Allow access to admin and maintenance page
            if (request.path.startswith('/admin/') or 
                request.path.startswith('/maintenance/') or
                (request.user.is_authenticated and request.user.is_superuser)):
                return None
            
            # Return maintenance page for everyone else
            from django.template.response import TemplateResponse
            return TemplateResponse(
                request,
                'maintenance.html',
                {'maintenance_message': 'Сайт тимчасово недоступний через технічні роботи'},
                status=503
            )
        
        return None


class AnalyticsMiddleware(MiddlewareMixin):
    """Basic analytics middleware for internal metrics"""
    
    def process_request(self, request):
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        # Log page views for important pages
        important_paths = ['/hub/', '/events/', '/account/', '/pricing/']
        
        if any(request.path.startswith(path) for path in important_paths):
            duration = getattr(request, '_start_time', None)
            if duration:
                duration = time.time() - duration
            
            # Log to analytics (simplified - would normally use Celery task)
            try:
                from apps.analytics.models import PageView
                PageView.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    path=request.path,
                    method=request.method,
                    status_code=response.status_code,
                    duration=duration,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    ip_address=self.get_client_ip(request)
                )
            except:
                # Fail silently - analytics shouldn't break the site
                pass
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')


class PhoneRegistrationMiddleware(MiddlewareMixin):
    """Middleware for handling phone-only registration limits and reminders"""
    
    def process_request(self, request):
        # Check phone registration limits before processing request
        if request.user.is_authenticated:
            return self.handle_phone_registration_limits(request)
        return None
    
    def handle_phone_registration_limits(self, request):
        """Handle 3-day phone registration limits and reminders"""
        user = request.user
        
        # Skip if user has verified email OR never registered via phone
        if user.is_email_verified or not user.phone_registered_at:
            return None
        
        # Check if phone registration expired
        if user.phone_registration_expired:
            from django.contrib.auth import logout
            from django.contrib import messages
            from django.shortcuts import redirect
            
            messages.error(request, 
                'Ваш 3-денний пробний період закінчився. Будь ласка, зареєструйтесь знову та підтвердіть email.')
            logout(request)
            return redirect('accounts:login')
        
        # Add reminder message ONLY for phone-only registration users
        if user.needs_email_verification:
            from django.contrib import messages
            days_left = 3 - user.days_since_phone_registration
            
            # Check if we haven't already added this message
            storage = messages.get_messages(request)
            existing_messages = [str(m) for m in storage]
            reminder_exists = any('Додайте email' in msg for msg in existing_messages)
            
            # Only show on specific pages to avoid spam
            show_on_pages = ['/account/', '/cabinet/', '/hub/', '/events/']
            should_show = any(request.path.startswith(page) for page in show_on_pages)
            
            if not reminder_exists and should_show:
                messages.warning(request, 
                    f'⚠️ Додайте email в особистому кабінеті та підтвердіть його. '
                    f'Залишилось днів: {days_left}')
        
        return None
