from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'categories', api_views.CategoryViewSet)
router.register(r'tags', api_views.TagViewSet)
router.register(r'courses', api_views.CourseViewSet)

app_name = 'content_api'

urlpatterns = [
    path('', include(router.urls)),
    
    # Course materials
    path('courses/<slug:course_slug>/materials/', 
         api_views.MaterialViewSet.as_view({'get': 'list'}), 
         name='course_materials'),
    path('courses/<slug:course_slug>/materials/<int:pk>/', 
         api_views.MaterialViewSet.as_view({'get': 'retrieve'}), 
         name='material_detail'),
    
    # Search
    path('search/', api_views.SearchAPIView.as_view(), name='search'),
    
    # User features
    path('favorites/', api_views.FavoritesAPIView.as_view(), name='favorites'),
    path('progress/', api_views.ProgressAPIView.as_view(), name='progress'),
    path('recommendations/', api_views.RecommendationsAPIView.as_view(), name='recommendations'),
    
    # Statistics
    path('stats/', api_views.StatsAPIView.as_view(), name='stats'),
]
