"""
HTMX URLs for content (hub navigation)
"""
from django.urls import path
from . import htmx_views

app_name = 'content_htmx'

urlpatterns = [
    path('hub/', htmx_views.HTMXCourseListView.as_view(), name='course_list'),
]

