"""
HTMX URLs for events navigation
"""
from django.urls import path
from . import htmx_views

app_name = 'events_htmx'

urlpatterns = [
    path('events/', htmx_views.HTMXEventListView.as_view(), name='event_list'),
]

