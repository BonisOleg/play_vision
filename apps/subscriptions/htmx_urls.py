"""
HTMX URLs for subscriptions navigation
"""
from django.urls import path
from . import htmx_views

app_name = 'subscriptions_htmx'

urlpatterns = [
    path('', htmx_views.HTMXPricingView.as_view(), name='pricing'),
]

