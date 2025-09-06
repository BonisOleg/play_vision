from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # Password reset
    path('password-reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # Verification
    path('verify/email/<str:code>/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('verify/phone/<str:code>/', views.VerifyPhoneView.as_view(), name='verify_phone'),
    
    # Profile
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    
    # Additional profile sections
    path('subscription/', views.SubscriptionView.as_view(), name='subscription'),
    path('courses/', views.MyCoursesView.as_view(), name='my_courses'),
    path('events/', views.MyEventsView.as_view(), name='my_events'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
]
