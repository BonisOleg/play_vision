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
    
    # Core pages
    path('', include('apps.core.urls')),
    
    # User authentication and accounts
    path('auth/', include('apps.accounts.urls')),
    path('account/', include(('apps.accounts.urls', 'accounts'), namespace='account')),  # Alternative URL for account pages
    
    # Main content
    path('hub/', include('apps.content.urls')),
    path('events/', include('apps.events.urls')),
    
    # Commerce
    path('cart/', include('apps.cart.urls')),
    path('payments/', include('apps.payments.urls')),
    
    # API endpoints (v1)
    path('api/v1/accounts/', include('apps.accounts.api_urls')),
    path('api/v1/content/', include('apps.content.api_urls')),
    path('api/v1/events/', include('apps.events.api_urls')),
    path('api/v1/cart/', include('apps.cart.api_urls')),
    
    # HTMX endpoints
    path('htmx/cart/', include('apps.cart.htmx_urls')),
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