"""
API URLs for notifications app
"""
from django.urls import path
from . import api_views

app_name = 'notifications-api'

urlpatterns = [
    # Push Notifications
    path('vapid-key/', api_views.VapidKeyView.as_view(), name='vapid_key'),
    path('push/subscribe/', api_views.PushSubscribeView.as_view(), name='push_subscribe'),
    path('push/unsubscribe/', api_views.PushUnsubscribeView.as_view(), name='push_unsubscribe'),
    
    # User notifications
    path('list/', api_views.NotificationListView.as_view(), name='notification_list'),
    path('<int:pk>/read/', api_views.MarkAsReadView.as_view(), name='mark_as_read'),
]