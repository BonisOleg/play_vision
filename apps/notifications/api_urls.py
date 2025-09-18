from django.urls import path
from . import api_views

app_name = 'notifications_api'

urlpatterns = [
    # Push notifications
    path('push/subscribe/', api_views.PushSubscribeAPIView.as_view(), name='push_subscribe'),
    path('push/unsubscribe/', api_views.PushUnsubscribeAPIView.as_view(), name='push_unsubscribe'),
    path('push/test/', api_views.PushTestAPIView.as_view(), name='push_test'),
    
    # Notification history
    path('history/', api_views.NotificationHistoryAPIView.as_view(), name='history'),
]
