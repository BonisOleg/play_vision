from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.shortcuts import get_object_or_404
import json

from .models import Event, Speaker, EventTicket, EventWaitlist, EventFeedback
from .serializers import (
    EventSerializer, EventDetailSerializer, SpeakerSerializer,
    EventTicketSerializer, EventRegistrationSerializer,
    EventFeedbackSerializer
)
# TODO: TicketBalance видалено - нова система підписок
# from apps.subscriptions.models import TicketBalance


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for events - read only for public API
    """
    queryset = Event.objects.filter(status='published')
    serializer_class = EventSerializer
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = Event.objects.filter(
            status='published'
        ).select_related('organizer').prefetch_related('speakers', 'tags')
        
        # Filter by upcoming/past
        time_filter = self.request.query_params.get('time')
        now = timezone.now()
        
        if time_filter == 'upcoming':
            queryset = queryset.filter(start_datetime__gt=now)
        elif time_filter == 'past':
            queryset = queryset.filter(start_datetime__lt=now)
        elif time_filter == 'ongoing':
            queryset = queryset.filter(
                start_datetime__lte=now,
                end_datetime__gte=now
            )
        
        # Filter by event type
        event_type = self.request.query_params.get('type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(speakers__first_name__icontains=search) |
                Q(speakers__last_name__icontains=search)
            ).distinct()
        
        # Featured only
        featured = self.request.query_params.get('featured')
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        return queryset.order_by('start_datetime')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EventDetailSerializer
        return EventSerializer
    
    @action(detail=True, methods=['get'])
    def tickets(self, request, slug=None):
        """Get tickets for specific event"""
        event = self.get_object()
        tickets = event.tickets.filter(status__in=['confirmed', 'used'])
        
        # Only event organizers or admins can see all tickets
        if not (request.user == event.organizer or request.user.is_staff):
            # Regular users can only see their own tickets
            if request.user.is_authenticated:
                tickets = tickets.filter(user=request.user)
            else:
                return Response(
                    {'detail': 'Authentication required'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
        
        serializer = EventTicketSerializer(tickets, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def feedback(self, request, slug=None):
        """Get feedback for specific event"""
        event = self.get_object()
        feedback = event.feedback.all()
        
        # Aggregate stats
        stats = feedback.aggregate(
            avg_overall=Avg('overall_rating'),
            avg_content=Avg('content_rating'),
            avg_speaker=Avg('speaker_rating'),
            avg_organization=Avg('organization_rating'),
            total_count=Count('id')
        )
        
        # Recent feedback
        recent_feedback = feedback.order_by('-created_at')[:10]
        
        return Response({
            'stats': stats,
            'recent_feedback': EventFeedbackSerializer(recent_feedback, many=True).data
        })


class SpeakerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for speakers
    """
    queryset = Speaker.objects.filter(is_active=True)
    serializer_class = SpeakerSerializer
    
    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        """Get events for specific speaker"""
        speaker = self.get_object()
        
        # Upcoming events
        upcoming = speaker.events.filter(
            status='published',
            start_datetime__gt=timezone.now()
        ).order_by('start_datetime')
        
        # Past events
        past = speaker.events.filter(
            status='published',
            start_datetime__lt=timezone.now()
        ).order_by('-start_datetime')[:10]
        
        return Response({
            'upcoming': EventSerializer(upcoming, many=True).data,
            'past': EventSerializer(past, many=True).data
        })


class EventTicketViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for event tickets - user can only see their own tickets
    """
    queryset = EventTicket.objects.all()
    serializer_class = EventTicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return EventTicket.objects.filter(
            user=self.request.user
        ).select_related('event', 'payment')


class RegisterForEventAPIView(APIView):
    """
    API view to register for an event
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, slug):
        event = get_object_or_404(Event, slug=slug, status='published')
        user = request.user
        
        # Check if can register
        can_register, message = event.can_register(user)
        if not can_register:
            return Response(
                {'error': message}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        use_balance = request.data.get('use_balance', False)
        
        if use_balance and event.requires_subscription:
            # TODO: Use new subscription system ticket balance
            # Temporarily treat as free event until new subscription system is integrated
            ticket = EventTicket.objects.create(
                event=event,
                user=user,
                status='confirmed',
                used_balance=True
            )
            
            # Update event stats
            event.tickets_sold += 1
            event.save()
            
            serializer = EventTicketSerializer(ticket)
            return Response({
                'message': f'Ви успішно зареєстровані на {event.title}!',
                'ticket': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        elif event.is_free:
            # Free event registration
            ticket = EventTicket.objects.create(
                event=event,
                user=user,
                status='confirmed'
            )
            
            event.tickets_sold += 1
            event.save()
            
            serializer = EventTicketSerializer(ticket)
            return Response({
                'message': f'Ви успішно зареєстровані на {event.title}!',
                'ticket': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        else:
            # Paid event - need to go through payment
            return Response({
                'message': 'Цей івент платний. Перейдіть до оплати.',
                'requires_payment': True,
                'price': float(event.price)
            }, status=status.HTTP_200_OK)


class JoinWaitlistAPIView(APIView):
    """
    API view to join event waitlist
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, slug):
        event = get_object_or_404(Event, slug=slug, status='published')
        user = request.user
        
        if not event.is_sold_out:
            return Response(
                {'error': 'Івент ще не розпроданий'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if event.waitlist.filter(user=user).exists():
            return Response(
                {'error': 'Ви вже в списку очікування'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        waitlist_entry = EventWaitlist.objects.create(
            event=event,
            user=user,
            email=user.email,
            phone=request.data.get('phone', '')
        )
        
        return Response({
            'message': 'Ви додані до списку очікування. Ми сповістимо вас про появу квитків.',
            'position': event.waitlist.filter(
                created_at__lte=waitlist_entry.created_at
            ).count()
        }, status=status.HTTP_201_CREATED)


class CalendarEventsAPIView(APIView):
    """
    API view for calendar events data
    """
    
    def get(self, request):
        start_date = request.query_params.get('start')
        end_date = request.query_params.get('end')
        event_type = request.query_params.get('type')
        
        # Base queryset
        events = Event.objects.filter(
            status='published'
        )
        
        if start_date:
            events = events.filter(start_datetime__gte=start_date)
        if end_date:
            events = events.filter(start_datetime__lte=end_date)
        if event_type and event_type != 'all':
            events = events.filter(event_type=event_type)
        
        # Format for calendar
        calendar_events = []
        for event in events:
            calendar_events.append({
                'id': event.id,
                'title': event.title,
                'start': event.start_datetime.isoformat(),
                'end': event.end_datetime.isoformat(),
                'url': event.get_absolute_url(),
                'className': f'event-{event.event_type}',
                'extendedProps': {
                    'type': event.get_event_type_display(),
                    'location': event.location,
                    'price': float(event.price) if not event.is_free else 0,
                    'isFree': event.is_free,
                    'availableTickets': event.available_tickets,
                    'isSoldOut': event.is_sold_out
                }
            })
        
        return Response(calendar_events)


class ValidateQRCodeAPIView(APIView):
    """
    API view to validate QR code
    """
    
    def post(self, request):
        qr_data = request.data.get('qr_data')
        
        if not qr_data:
            return Response(
                {'valid': False, 'error': 'QR дані відсутні'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Decode QR data
            decoded_data = json.loads(qr_data)
            ticket_id = decoded_data.get('ticket_id')
            
            if not ticket_id:
                return Response({
                    'valid': False,
                    'error': 'Невірний QR код'
                })
            
            ticket = EventTicket.objects.get(id=ticket_id)
            
            # Validate QR data
            if not ticket.validate_qr_data(qr_data):
                return Response({
                    'valid': False,
                    'error': 'Підроблений QR код'
                })
            
            # Check ticket status
            if ticket.status == 'used':
                return Response({
                    'valid': False,
                    'error': f'Квиток вже використаний {ticket.used_at.strftime("%d.%m.%Y %H:%M")}',
                    'used_at': ticket.used_at.isoformat()
                })
            
            if ticket.status != 'confirmed':
                return Response({
                    'valid': False,
                    'error': 'Квиток не підтверджений'
                })
            
            # Check event timing
            if not ticket.event.is_ongoing and not ticket.event.is_upcoming:
                return Response({
                    'valid': False,
                    'error': 'Івент завершений'
                })
            
            return Response({
                'valid': True,
                'ticket': {
                    'number': ticket.ticket_number,
                    'event': ticket.event.title,
                    'user': ticket.user.profile.full_name if hasattr(ticket.user, 'profile') else ticket.user.email,
                    'event_start': ticket.event.start_datetime.isoformat()
                }
            })
            
        except (json.JSONDecodeError, ValueError, EventTicket.DoesNotExist):
            return Response({
                'valid': False,
                'error': 'Квиток не знайдено'
            })


class CheckInTicketAPIView(APIView):
    """
    API view to check in ticket
    """
    
    def post(self, request):
        qr_data = request.data.get('qr_data')
        
        if not qr_data:
            return Response(
                {'success': False, 'error': 'QR дані відсутні'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Decode and find ticket
            decoded_data = json.loads(qr_data)
            ticket = EventTicket.objects.get(id=decoded_data.get('ticket_id'))
            
            # Validate QR
            if not ticket.validate_qr_data(qr_data):
                return Response({
                    'success': False,
                    'error': 'Підроблений QR код'
                })
            
            # Check in
            checked_by = request.user if request.user.is_authenticated else None
            success, message = ticket.check_in(checked_by)
            
            if success:
                return Response({
                    'success': True,
                    'message': message,
                    'ticket': {
                        'number': ticket.ticket_number,
                        'user': ticket.user.profile.full_name if hasattr(ticket.user, 'profile') else ticket.user.email,
                        'checked_in_at': ticket.used_at.isoformat()
                    }
                })
            else:
                return Response({
                    'success': False,
                    'error': message
                })
                
        except (json.JSONDecodeError, ValueError, EventTicket.DoesNotExist):
            return Response({
                'success': False,
                'error': 'Квиток не знайдено'
            })
