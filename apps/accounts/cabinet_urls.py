"""
URL patterns for user cabinet functionality
"""
from django.urls import path
from . import views

app_name = 'accounts_cabinet'

urlpatterns = [
    # Dashboard and main cabinet page
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Profile management
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    
    # Subscription management
    path('subscription/', views.SubscriptionView.as_view(), name='subscription'),
    
    # User content and files
    path('files/', views.MyFilesView.as_view(), name='files'),
    path('courses/', views.MyCoursesView.as_view(), name='courses'),
    path('events/', views.MyEventsView.as_view(), name='events'),
    
    # Payment history
    path('payments/', views.PaymentHistoryView.as_view(), name='payments'),
    
    # Loyalty program
    path('loyalty/', views.LoyaltyView.as_view(), name='loyalty'),
    
    # Settings
    path('settings/', views.SettingsView.as_view(), name='settings'),
]
