"""
HTMX URLs for cross-app compatibility
"""
from django.urls import path, include

app_name = 'htmx'

urlpatterns = [
    # Cart HTMX endpoints
    path('cart/', include('apps.cart.htmx_urls', namespace='cart')),
]
