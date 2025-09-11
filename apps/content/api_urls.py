from django.urls import path
from . import api_views

app_name = 'content_api'

urlpatterns = [
    # Material progress tracking
    path('material/progress/', api_views.MaterialProgressAPIView.as_view(), name='material_progress'),
    
    # Course progress tracking  
    path('course/<int:course_id>/progress/', api_views.CourseProgressAPIView.as_view(), name='course_progress'),
    
    # Search suggestions
    path('search/suggestions/', api_views.SearchSuggestionsAPIView.as_view(), name='search_suggestions'),
    
    # User favorites
    path('favorites/', api_views.UserFavoritesAPIView.as_view(), name='user_favorites'),
    
    # Course analytics (admin)
    path('course/<int:course_id>/analytics/', api_views.CourseAnalyticsAPIView.as_view(), name='course_analytics'),
]
