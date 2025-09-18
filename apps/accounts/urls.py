from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
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
    
    # Email management
    path('add-email/', views.AddEmailView.as_view(), name='add_email'),
    path('verify-email-form/', views.VerifyEmailFormView.as_view(), name='verify_email_form'),
    path('verify-email/', views.VerifyEmailFormView.as_view(), name='verify_email_universal'),
    
    # Redirects from old URLs to new cabinet
    path('profile/', RedirectView.as_view(pattern_name='cabinet:profile', permanent=True), name='profile'),
    path('profile/edit/', RedirectView.as_view(pattern_name='cabinet:profile', permanent=True), name='profile_edit'),
    path('subscription/', RedirectView.as_view(pattern_name='cabinet:subscription', permanent=True), name='subscription'),
    path('courses/', RedirectView.as_view(pattern_name='cabinet:courses', permanent=True), name='my_courses'),
    path('events/', RedirectView.as_view(pattern_name='cabinet:events', permanent=True), name='my_events'),
    path('settings/', RedirectView.as_view(pattern_name='cabinet:settings', permanent=True), name='settings'),
]
