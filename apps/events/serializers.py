from rest_framework import serializers
from .models import Event, Speaker, EventTicket, EventRegistration, EventFeedback
from apps.accounts.serializers import UserBasicSerializer


class SpeakerSerializer(serializers.ModelSerializer):
    """Serializer for Speaker model"""
    full_name = serializers.ReadOnlyField()
    photo_url = serializers.ReadOnlyField(source='get_photo_url')
    
    class Meta:
        model = Speaker
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 
            'bio', 'position', 'company', 'photo_url',
            'linkedin_url', 'twitter_url', 'website_url'
        ]


class EventSerializer(serializers.ModelSerializer):
    """Basic serializer for Event model"""
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    organizer_name = serializers.CharField(source='organizer.profile.full_name', read_only=True)
    duration_minutes = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    is_ongoing = serializers.ReadOnlyField()
    is_sold_out = serializers.ReadOnlyField()
    available_tickets = serializers.ReadOnlyField()
    is_online = serializers.ReadOnlyField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'short_description', 'event_type', 
            'event_type_display', 'status', 'status_display',
            'start_datetime', 'end_datetime', 'timezone_name',
            'location', 'is_online', 'max_attendees', 'tickets_sold',
            'price', 'is_free', 'requires_subscription',
            'thumbnail', 'organizer_name', 'is_featured',
            'duration_minutes', 'is_upcoming', 'is_ongoing',
            'is_sold_out', 'available_tickets', 'created_at'
        ]


class EventDetailSerializer(EventSerializer):
    """Detailed serializer for Event model"""
    speakers = SpeakerSerializer(many=True, read_only=True)
    tags = serializers.StringRelatedField(many=True, read_only=True)
    organizer = UserBasicSerializer(read_only=True)
    
    class Meta(EventSerializer.Meta):
        fields = EventSerializer.Meta.fields + [
            'description', 'online_link', 'banner_image',
            'speakers', 'tags', 'organizer', 'requires_approval',
            'send_reminders', 'meta_title', 'meta_description'
        ]


class EventTicketSerializer(serializers.ModelSerializer):
    """Serializer for EventTicket model"""
    event = EventSerializer(read_only=True)
    user = UserBasicSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = EventTicket
        fields = [
            'id', 'ticket_number', 'status', 'status_display',
            'event', 'user', 'used_balance', 'qr_code',
            'used_at', 'created_at'
        ]


class EventRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for EventRegistration model"""
    ticket = EventTicketSerializer(read_only=True)
    
    class Meta:
        model = EventRegistration
        fields = [
            'ticket', 'dietary_requirements', 'special_needs',
            'emergency_contact', 'emergency_phone', 'how_did_you_hear',
            'marketing_consent', 'custom_fields', 'created_at'
        ]


class EventFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for EventFeedback model"""
    user_name = serializers.CharField(source='user.profile.full_name', read_only=True)
    
    class Meta:
        model = EventFeedback
        fields = [
            'overall_rating', 'content_rating', 'speaker_rating',
            'organization_rating', 'what_liked', 'what_could_improve',
            'additional_comments', 'would_recommend', 'would_attend_again',
            'user_name', 'created_at'
        ]


class EventRegistrationRequestSerializer(serializers.Serializer):
    """Serializer for event registration request"""
    use_balance = serializers.BooleanField(default=False)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    dietary_requirements = serializers.CharField(required=False, allow_blank=True)
    special_needs = serializers.CharField(required=False, allow_blank=True)
    emergency_contact = serializers.CharField(max_length=100, required=False, allow_blank=True)
    emergency_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    how_did_you_hear = serializers.CharField(max_length=100, required=False, allow_blank=True)
    marketing_consent = serializers.BooleanField(default=False)


class QRValidationSerializer(serializers.Serializer):
    """Serializer for QR code validation"""
    qr_data = serializers.CharField()


class EventCalendarSerializer(serializers.Serializer):
    """Serializer for calendar events"""
    start = serializers.DateTimeField(required=False)
    end = serializers.DateTimeField(required=False)
    type = serializers.CharField(required=False)
