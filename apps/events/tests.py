from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Event, Speaker, EventTicket

User = get_user_model()


class EventModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='organizer@test.com',
            password='testpass123'
        )
        
        self.event = Event.objects.create(
            title='Test Event',
            description='Test Description',
            short_description='Short desc',
            event_type='webinar',
            start_datetime=timezone.now() + timedelta(days=7),
            end_datetime=timezone.now() + timedelta(days=7, hours=2),
            location='Online',
            max_attendees=100,
            price=500.00,
            organizer=self.user
        )
    
    def test_event_creation(self):
        """Test event creation and slug generation"""
        self.assertEqual(self.event.title, 'Test Event')
        self.assertEqual(self.event.slug, 'test-event')
        self.assertTrue(self.event.is_upcoming)
        self.assertFalse(self.event.is_sold_out)
    
    def test_can_register(self):
        """Test registration validation"""
        # Published event should allow registration
        self.event.status = 'published'
        self.event.save()
        
        can_register, message = self.event.can_register()
        self.assertTrue(can_register)
        
        # Sold out event should not allow registration
        self.event.tickets_sold = self.event.max_attendees
        self.event.save()
        
        can_register, message = self.event.can_register()
        self.assertFalse(can_register)
        self.assertIn("продані", message)


class EventTicketTest(TestCase):
    def setUp(self):
        self.organizer = User.objects.create_user(
            email='organizer@test.com',
            password='testpass123'
        )
        
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123'
        )
        
        self.event = Event.objects.create(
            title='Test Event',
            description='Test Description',
            short_description='Short desc',
            event_type='webinar',
            start_datetime=timezone.now() + timedelta(days=7),
            end_datetime=timezone.now() + timedelta(days=7, hours=2),
            location='Online',
            max_attendees=100,
            price=500.00,
            organizer=self.organizer,
            status='published'
        )
    
    def test_ticket_creation(self):
        """Test ticket creation and QR generation"""
        ticket = EventTicket.objects.create(
            event=self.event,
            user=self.user,
            status='confirmed'
        )
        
        self.assertIsNotNone(ticket.ticket_number)
        self.assertEqual(len(ticket.ticket_number), 8)
    
    def test_ticket_check_in(self):
        """Test ticket check-in process"""
        ticket = EventTicket.objects.create(
            event=self.event,
            user=self.user,
            status='confirmed'
        )
        
        # Check in should work
        success, message = ticket.check_in(self.organizer)
        self.assertTrue(success)
        self.assertEqual(ticket.status, 'used')
        self.assertIsNotNone(ticket.used_at)
        
        # Second check in should fail
        success, message = ticket.check_in(self.organizer)
        self.assertFalse(success)
        self.assertIn("використаний", message)
