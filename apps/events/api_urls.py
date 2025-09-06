from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'events', api_views.EventViewSet)
router.register(r'speakers', api_views.SpeakerViewSet)
router.register(r'tickets', api_views.EventTicketViewSet)

app_name = 'events_api'

urlpatterns = [
    path('', include(router.urls)),
    
    # Custom API endpoints
    path('events/<slug:slug>/register/', api_views.RegisterForEventAPIView.as_view(), name='register_event'),
    path('events/<slug:slug>/waitlist/', api_views.JoinWaitlistAPIView.as_view(), name='join_waitlist'),
    path('calendar/', api_views.CalendarEventsAPIView.as_view(), name='calendar_events'),
    path('qr/validate/', api_views.ValidateQRCodeAPIView.as_view(), name='validate_qr'),
    path('qr/checkin/', api_views.CheckInTicketAPIView.as_view(), name='checkin_ticket'),
]
