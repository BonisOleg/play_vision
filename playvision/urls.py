"""
URL configuration for playvision project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # ========================================
    # DOMAIN-BASED ROUTING via DomainRoutingMiddleware
    # playvision.com.ua → Landing (handled by middleware)
    # playvision.onrender.com → Core site
    # ========================================
    path('', include('apps.core.urls')),  # Core site (default)
    path('', include('apps.landing.urls')),  # Landing (when middleware routes to it)
    
    # User authentication and accounts
    path('auth/', include('apps.accounts.urls')),
    
    # Personal cabinet (separate namespace to avoid conflicts)
    path('account/', include('apps.accounts.cabinet_urls', namespace='cabinet')),
    
    # Main content
    path('hub/', include('apps.content.urls')),
    path('events/', include('apps.events.urls')),
    
    # AI Assistant
    path('ai/', include('apps.ai.urls')),
    
    # Commerce
    # Нова система підписок
    path('', include('apps.subscriptions.urls')),
    path('cart/', include('apps.cart.urls')),
    path('payments/', include('apps.payments.urls')),
    path('loyalty/', include('apps.loyalty.urls')),
    
    # API endpoints (v1)
    path('api/v1/accounts/', include('apps.accounts.api_urls')),
    path('api/v1/content/', include('apps.content.api_urls')),
    path('api/v1/events/', include('apps.events.api_urls')),
    path('api/v1/cart/', include('apps.cart.api_urls')),
    path('api/v1/notifications/', include('apps.notifications.api_urls')),
    
    # HTMX endpoints
    path('htmx/', include('apps.core.htmx_urls')),
    path('htmx/cart/', include('apps.cart.htmx_urls')),
    
    # Video Security (НОВИЙ)
    path('video-security/', include('apps.video_security.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Django Debug Toolbar
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
    
    # Django Silk profiling
    try:
        urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
    except ImportError:
        pass