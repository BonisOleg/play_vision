from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    # Event listing and details
    path('', views.EventListView.as_view(), name='event_list'),
    path('calendar/', views.event_calendar_data, name='calendar_data'),
    path('<slug:slug>/', views.EventDetailView.as_view(), name='event_detail'),
    
    # Registration actions
    path('<slug:slug>/register/', views.event_register, name='register'),
    path('<slug:slug>/register-free/', views.register_free_event, name='register_free'),
    path('<slug:slug>/waitlist/', views.join_waitlist, name='join_waitlist'),
    path('<slug:slug>/cancel/', views.cancel_registration, name='cancel_registration'),
    path('<slug:slug>/feedback/', views.submit_feedback, name='submit_feedback'),
    
    # QR code validation (for event staff)
    path('qr/validate/', views.validate_qr_code, name='validate_qr'),
    path('qr/checkin/', views.check_in_ticket, name='checkin_ticket'),
    
    # Speakers
    path('speakers/', views.SpeakerListView.as_view(), name='speaker_list'),
    path('speakers/<int:speaker_id>/', views.SpeakerDetailView.as_view(), name='speaker_detail'),
]
