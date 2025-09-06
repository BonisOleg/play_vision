from django.urls import path
from . import api_views

app_name = 'accounts_api'

urlpatterns = [
    # Authentication
    path('check-email/', api_views.CheckEmailView.as_view(), name='check_email'),
    path('register/', api_views.UserRegistrationAPIView.as_view(), name='register'),
    path('login/', api_views.UserLoginAPIView.as_view(), name='login'),
    path('logout/', api_views.UserLogoutAPIView.as_view(), name='logout'),
    
    # Password management
    path('password/change/', api_views.PasswordChangeAPIView.as_view(), name='password_change'),
    path('password/reset/', api_views.PasswordResetRequestAPIView.as_view(), name='password_reset'),
    path('password/reset/confirm/', api_views.PasswordResetConfirmAPIView.as_view(), name='password_reset_confirm'),
    
    # Verification
    path('verification/send/', api_views.SendVerificationCodeAPIView.as_view(), name='send_verification'),
    path('verification/verify/', api_views.VerifyCodeAPIView.as_view(), name='verify_code'),
    path('verify-code/', api_views.VerifyCodeView.as_view(), name='verify_code_legacy'),  # Legacy endpoint
    
    # Profile management
    path('profile/', api_views.UserProfileAPIView.as_view(), name='profile'),
    path('subscription/', api_views.UserSubscriptionInfoAPIView.as_view(), name='subscription_info'),
    path('courses/', api_views.UserCoursesAPIView.as_view(), name='user_courses'),
    path('events/', api_views.UserEventsAPIView.as_view(), name='user_events'),
    
    # Account management
    path('delete/', api_views.delete_user_account, name='delete_account'),
]