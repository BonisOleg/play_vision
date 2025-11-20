from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from datetime import timedelta
import json

from .models import Event, EventTicket, EventWaitlist, EventFeedback, Speaker, EventRegistration
# TODO: Видалено TicketBalance - буде нова система підписок
# # TODO: TicketBalance видалено - нова система підписок
# from apps.subscriptions.models import TicketBalance


class EventListView(ListView):
    """List view for events"""
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Event.objects.filter(
            status='published',
            start_datetime__gt=timezone.now()
        ).select_related('organizer').prefetch_related('speakers')
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(event_category=category)
        
        # Filter by type (підтримуємо множинні значення через чекбокси)
        event_types = self.request.GET.getlist('type')
        # Фільтруємо 'all' якщо воно є у списку
        event_types = [t for t in event_types if t and t != 'all']
        
        if event_types:
            queryset = queryset.filter(event_type__in=event_types)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(speakers__first_name__icontains=search) |
                Q(speakers__last_name__icontains=search)
            ).distinct()
        
        # Filter by format (online/offline)
        format_filter = self.request.GET.get('format')
        if format_filter and format_filter != 'all':
            if format_filter == 'online':
                queryset = queryset.filter(is_online_event=True)
            elif format_filter == 'offline':
                queryset = queryset.filter(is_online_event=False)
        
        # Filter by date range
        date_range = self.request.GET.get('date_range')
        now = timezone.now()
        if date_range == 'today':
            queryset = queryset.filter(start_datetime__date=now.date())
        elif date_range == 'week':
            week_end = now + timezone.timedelta(days=7)
            queryset = queryset.filter(start_datetime__range=[now, week_end])
        elif date_range == 'month':
            month_end = now + timezone.timedelta(days=30)
            queryset = queryset.filter(start_datetime__range=[now, month_end])
        
        # Ordering
        order = self.request.GET.get('order', 'start_datetime')
        if order in ['start_datetime', '-start_datetime', 'price', '-price', 'title']:
            queryset = queryset.order_by(order)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event_types'] = Event.EVENT_TYPE_CHOICES
        # Отримуємо всі вибрані типи (підтримка множинного вибору)
        current_types = self.request.GET.getlist('type')
        # Фільтруємо 'all' якщо воно є
        current_types = [t for t in current_types if t and t != 'all']
        context['current_types'] = current_types
        context['current_search'] = self.request.GET.get('search', '')
        context['current_format'] = self.request.GET.get('format', 'all')
        context['current_date_range'] = self.request.GET.get('date_range', 'all')
        context['current_order'] = self.request.GET.get('order', 'start_datetime')
        
        # Get display names for current types
        types_dict = dict(Event.EVENT_TYPE_CHOICES)
        context['current_types_display'] = [
            types_dict.get(t) for t in context['current_types'] if t in types_dict
        ]
        
        # Featured events
        context['featured_events'] = Event.objects.filter(
            status='published',
            is_featured=True,
            start_datetime__gt=timezone.now()
        )[:3]
        
        # Генерація календаря-тижня
        week_offset = int(self.request.GET.get('week', 0))
        base_date = timezone.now().date()
        start_date = base_date + timedelta(weeks=week_offset)
        
        # Знайти понеділок цього тижня
        start_of_week = start_date - timedelta(days=start_date.weekday())
        
        # Згенерувати 7 днів
        calendar_days = []
        day_names = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Нд']
        
        for day_offset in range(7):
            current_date = start_of_week + timedelta(days=day_offset)
            
            # Знайти ПЕРШУ подію цього дня
            event = Event.objects.filter(
                status='published',
                start_datetime__date=current_date
            ).select_related('organizer').first()
            
            calendar_days.append({
                'date': current_date,
                'day_number': current_date.day,
                'day_name': day_names[day_offset],
                'event': event,
                'is_today': current_date == base_date
            })
        
        context['calendar_days'] = calendar_days
        context['week_offset'] = week_offset
        context['week_start'] = start_of_week
        context['week_end'] = start_of_week + timedelta(days=6)
        
        return context


class EventDetailView(DetailView):
    """Detail view for single event"""
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'
    
    def get_queryset(self):
        return Event.objects.filter(
            status='published'
        ).select_related('organizer').prefetch_related(
            'speakers', 'tickets__user'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object
        user = self.request.user
        
        # Check user registration status
        if user.is_authenticated:
            context['user_ticket'] = event.tickets.filter(
                user=user, status__in=['confirmed', 'used']
            ).first()
            context['user_in_waitlist'] = event.waitlist.filter(user=user).exists()
            
            # Check available ticket balance (temporarily disabled - new subscription system)
            # TODO: Integrate with new subscription system when ready
            context['ticket_balance'] = 0
            context['has_ticket_balance'] = False
        
        # Registration status
        context['can_register'], context['register_message'] = event.can_register(user if user.is_authenticated else None)
        
        # Structured ticket tiers for template
        context['structured_tiers'] = event.ticket_tiers if event.ticket_tiers else []
        
        # Рекомендовані події (5 івентів що можуть бути цікавими)
        # Спочатку шукаємо події того ж типу, потім інші майбутні події
        recommended = Event.objects.filter(
            status='published',
            start_datetime__gt=timezone.now(),
            event_type=event.event_type
        ).exclude(id=event.id)[:5]
        
        # Якщо менше 5 подій того ж типу, додаємо інші події
        if recommended.count() < 5:
            additional_events = Event.objects.filter(
                status='published',
                start_datetime__gt=timezone.now()
            ).exclude(
                id__in=[event.id] + list(recommended.values_list('id', flat=True))
            )[:5 - recommended.count()]
            
            recommended = list(recommended) + list(additional_events)
        
        context['recommended_events'] = recommended
        
        # Feedback stats
        feedback_stats = event.feedback.aggregate(
            avg_rating=Avg('overall_rating'),
            count=Count('id')
        )
        context['avg_rating'] = feedback_stats['avg_rating']
        context['feedback_count'] = feedback_stats['count']
        
        return context


@login_required
@require_POST
def register_for_event(request, slug):
    """Register user for event"""
    event = get_object_or_404(Event, slug=slug, status='published')
    user = request.user
    
    # Check if can register
    can_register, message = event.can_register(user)
    if not can_register:
        messages.error(request, message)
        return redirect('events:event_detail', slug=slug)
    
    # Check payment method
    payment_method = request.POST.get('payment_method', 'purchase')
    tier_name = request.POST.get('tier_name', '')
    use_balance = payment_method == 'balance'
    
    if use_balance and event.requires_subscription:
        # TODO: Use new subscription system ticket balance
        # Temporarily treat as free event until new subscription system is integrated
        ticket = EventTicket.objects.create(
            event=event,
            user=user,
            status='confirmed',
            used_balance=True,
            tier_name=tier_name
        )
        
        # Update event stats
        event.tickets_sold += 1
        event.save()
        
        messages.success(request, f'Ви успішно зареєстровані на {event.title}!')
        return redirect('accounts:profile')
    
    elif event.is_free:
        # Free event registration
        ticket = EventTicket.objects.create(
            event=event,
            user=user,
            status='confirmed',
            tier_name=tier_name
        )
        
        event.tickets_sold += 1
        event.save()
        
        messages.success(request, f'Ви успішно зареєстровані на {event.title}!')
        return redirect('accounts:profile')
    
    else:
        # Paid event - redirect to cart
        # Add event ticket to cart
        from apps.cart.services import CartService
        cart_service = CartService(request)
        cart_service.add_event_ticket(event, tier_name)
        
        messages.info(request, f'Квиток на {event.title} додано до кошика')
        return redirect('cart:cart')


@login_required
@require_POST
def join_waitlist(request, slug):
    """Join event waitlist"""
    event = get_object_or_404(Event, slug=slug, status='published')
    user = request.user
    
    if not event.is_sold_out:
        messages.error(request, 'Івент ще не розпроданий')
        return redirect('events:event_detail', slug=slug)
    
    if event.waitlist.filter(user=user).exists():
        messages.warning(request, 'Ви вже в списку очікування')
        return redirect('events:event_detail', slug=slug)
    
    EventWaitlist.objects.create(
        event=event,
        user=user,
        email=user.email,
        phone=user.profile.phone if hasattr(user, 'profile') else ''
    )
    
    messages.success(request, 'Ви додані до списку очікування. Ми сповістимо вас про появу квитків.')
    return redirect('events:event_detail', slug=slug)


@login_required
@require_POST
def cancel_registration(request, slug):
    """Cancel event registration"""
    event = get_object_or_404(Event, slug=slug)
    user = request.user
    
    ticket = get_object_or_404(
        EventTicket,
        event=event,
        user=user,
        status__in=['confirmed', 'pending']
    )
    
    success, message = ticket.cancel()
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('accounts:profile')


@csrf_exempt
@require_POST
def validate_qr_code(request):
    """Validate QR code for event check-in"""
    try:
        data = json.loads(request.body)
        qr_data = data.get('qr_data')
        
        if not qr_data:
            return JsonResponse({'valid': False, 'error': 'QR дані відсутні'})
        
        # Decode QR data
        try:
            decoded_data = json.loads(qr_data)
            ticket_id = decoded_data.get('ticket_id')
            
            if not ticket_id:
                return JsonResponse({'valid': False, 'error': 'Невірний QR код'})
            
            ticket = EventTicket.objects.get(id=ticket_id)
            
            # Validate QR data
            if not ticket.validate_qr_data(qr_data):
                return JsonResponse({'valid': False, 'error': 'Підроблений QR код'})
            
            # Check ticket status
            if ticket.status == 'used':
                return JsonResponse({
                    'valid': False,
                    'error': f'Квиток вже використаний {ticket.used_at.strftime("%d.%m.%Y %H:%M")}',
                    'used_at': ticket.used_at.isoformat()
                })
            
            if ticket.status != 'confirmed':
                return JsonResponse({'valid': False, 'error': 'Квиток не підтверджений'})
            
            # Check event timing
            if not ticket.event.is_ongoing and not ticket.event.is_upcoming:
                return JsonResponse({'valid': False, 'error': 'Івент завершений'})
            
            return JsonResponse({
                'valid': True,
                'ticket': {
                    'number': ticket.ticket_number,
                    'event': ticket.event.title,
                    'user': ticket.user.profile.full_name if hasattr(ticket.user, 'profile') else ticket.user.email,
                    'event_start': ticket.event.start_datetime.isoformat()
                }
            })
            
        except (json.JSONDecodeError, ValueError, EventTicket.DoesNotExist):
            return JsonResponse({'valid': False, 'error': 'Квиток не знайдено'})
        
    except json.JSONDecodeError:
        return JsonResponse({'valid': False, 'error': 'Невірний формат даних'})


@csrf_exempt
@require_POST
def check_in_ticket(request):
    """Check in ticket at event"""
    try:
        data = json.loads(request.body)
        qr_data = data.get('qr_data')
        
        if not qr_data:
            return JsonResponse({'success': False, 'error': 'QR дані відсутні'})
        
        # Decode and find ticket
        try:
            decoded_data = json.loads(qr_data)
            ticket = EventTicket.objects.get(id=decoded_data.get('ticket_id'))
            
            # Validate QR
            if not ticket.validate_qr_data(qr_data):
                return JsonResponse({'success': False, 'error': 'Підроблений QR код'})
            
            # Check in
            success, message = ticket.check_in()
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': message,
                    'ticket': {
                        'number': ticket.ticket_number,
                        'user': ticket.user.profile.full_name if hasattr(ticket.user, 'profile') else ticket.user.email,
                        'checked_in_at': ticket.used_at.isoformat()
                    }
                })
            else:
                return JsonResponse({'success': False, 'error': message})
                
        except (json.JSONDecodeError, ValueError, EventTicket.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'Квиток не знайдено'})
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Невірний формат даних'})


def event_calendar_data(request):
    """Get events data for calendar"""
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    event_type = request.GET.get('type')
    
    # Base queryset
    events = Event.objects.filter(
        status='published',
        start_datetime__gte=start_date,
        start_datetime__lte=end_date
    )
    
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
    
    return JsonResponse(calendar_events, safe=False)


class SpeakerListView(ListView):
    """List view for speakers"""
    model = Speaker
    template_name = 'events/speaker_list.html'
    context_object_name = 'speakers'
    paginate_by = 12
    
    def get_queryset(self):
        return Speaker.objects.filter(is_active=True).order_by('last_name', 'first_name')


class SpeakerDetailView(DetailView):
    """Detail view for speaker"""
    model = Speaker
    template_name = 'events/speaker_detail.html'
    context_object_name = 'speaker'
    slug_field = 'id'
    slug_url_kwarg = 'speaker_id'
    
    def get_queryset(self):
        return Speaker.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        speaker = self.object
        
        # Speaker's upcoming events
        context['upcoming_events'] = speaker.events.filter(
            status='published',
            start_datetime__gt=timezone.now()
        ).order_by('start_datetime')[:5]
        
        # Speaker's past events
        context['past_events'] = speaker.events.filter(
            status='published',
            start_datetime__lt=timezone.now()
        ).order_by('-start_datetime')[:5]
        
        return context


@login_required
@require_POST
def submit_feedback(request, slug):
    """Submit feedback for completed event"""
    event = get_object_or_404(Event, slug=slug)
    user = request.user
    
    # Check if user attended the event
    ticket = get_object_or_404(
        EventTicket,
        event=event,
        user=user,
        status='used'
    )
    
    # Check if feedback already exists
    if EventFeedback.objects.filter(event=event, user=user).exists():
        messages.warning(request, 'Ви вже залишили відгук для цього івенту')
        return redirect('events:event_detail', slug=slug)
    
    try:
        feedback = EventFeedback.objects.create(
            event=event,
            user=user,
            overall_rating=int(request.POST.get('overall_rating')),
            content_rating=int(request.POST.get('content_rating')),
            speaker_rating=int(request.POST.get('speaker_rating')),
            organization_rating=int(request.POST.get('organization_rating')),
            what_liked=request.POST.get('what_liked', ''),
            what_could_improve=request.POST.get('what_could_improve', ''),
            additional_comments=request.POST.get('additional_comments', ''),
            would_recommend=request.POST.get('would_recommend') == 'on',
            would_attend_again=request.POST.get('would_attend_again') == 'on'
        )
        
        messages.success(request, 'Дякуємо за ваш відгук!')
        
    except (ValueError, TypeError):
        messages.error(request, 'Помилка в заповненні форми відгуку')
    
    return redirect('events:event_detail', slug=slug)


def event_register(request, slug):
    """Register for an event"""
    event = get_object_or_404(Event, slug=slug, status='published')
    
    if not request.user.is_authenticated:
        messages.error(request, 'Необхідно увійти для реєстрації')
        return redirect('accounts:login')
    
    if request.method == 'POST':
        # Check if already registered
        if EventTicket.objects.filter(event=event, user=request.user).exists():
            messages.info(request, 'Ви вже зареєстровані на цю подію')
            return redirect('events:event_detail', slug=slug)
        
        # Check capacity
        if event.tickets_sold >= event.max_attendees:
            messages.error(request, 'На жаль, всі місця зайняті')
            return redirect('events:event_detail', slug=slug)
        
        # Get form data
        name = request.POST.get('name', request.user.get_full_name() or request.user.username)
        email = request.POST.get('email', request.user.email)
        phone = request.POST.get('phone', '')
        
        # Create ticket
        ticket = EventTicket.objects.create(
            event=event,
            user=request.user,
            price=event.price if not event.is_free else 0,
            ticket_number=f"EVT{event.id:04d}{request.user.id:04d}"
        )
        
        # Create registration
        EventRegistration.objects.create(
            event=event,
            user=request.user,
            ticket=ticket,
            attendee_name=name,
            attendee_email=email,
            attendee_phone=phone,
            company=request.POST.get('company', ''),
            position=request.POST.get('position', ''),
            notes=request.POST.get('expectations', '')
        )
        
        # Update tickets sold
        event.tickets_sold += 1
        event.save()
        
        messages.success(request, 'Ви успішно зареєструвалися на подію!')
        
        # If paid event, redirect to payment
        if not event.is_free:
            return redirect('payments:checkout', item_type='ticket', item_id=ticket.id)
        
        return redirect('events:event_detail', slug=slug)
    
    # GET request - show registration form
    context = {
        'event': event
    }
    return render(request, 'events/event_registration_form.html', context)
