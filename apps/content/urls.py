from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    # Course catalog
    path('', views.CourseListView.as_view(), name='course_list'),
    path('course/<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('search/', views.CourseSearchView.as_view(), name='course_search'),
    
    # Course materials
    path('course/<slug:course_slug>/material/<slug:material_slug>/', 
         views.MaterialDetailView.as_view(), name='material_detail'),
    
    # User actions
    path('course/<int:pk>/favorite/', views.ToggleFavoriteView.as_view(), name='toggle_favorite'),
    path('course/<int:pk>/progress/', views.UpdateProgressView.as_view(), name='update_progress'),
]
