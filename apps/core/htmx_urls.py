"""
HTMX URLs for cross-app compatibility
"""
from django.urls import path, include
from . import htmx_views

app_name = 'htmx'

urlpatterns = [
    # Cart HTMX endpoints
    path('cart/', include('apps.cart.htmx_urls', namespace='cart')),
    
    # Pages HTMX endpoints (for navigation)
    path('pages/home/', htmx_views.HTMXHomeView.as_view(), name='pages_home'),
    path('pages/about/', htmx_views.HTMXAboutView.as_view(), name='pages_about'),
    path('pages/mentoring/', htmx_views.HTMXMentoringView.as_view(), name='pages_mentoring'),
]
