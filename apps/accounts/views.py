from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.views.generic import CreateView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.utils import timezone
from django.db import models
from datetime import timedelta
from .models import User, Profile, VerificationCode
from .forms import CustomUserCreationForm, ProfileForm


class CustomLoginView(LoginView):
    """Custom login view with email support"""
    template_name = 'auth/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('accounts:profile')


class RegisterView(CreateView):
    """User registration view"""
    model = User
    form_class = CustomUserCreationForm
    template_name = 'auth/register.html'
    success_url = reverse_lazy('accounts:profile')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Create user profile
        Profile.objects.create(user=self.object)
        
        # Send verification email
        self.send_verification_email()
        
        # Auto login
        login(self.request, self.object)
        
        messages.success(self.request, 'Вітаємо! Ваш акаунт успішно створено.')
        return response
    
    def send_verification_email(self):
        """Send email verification code"""
        import random
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        VerificationCode.objects.create(
            user=self.object,
            code=code,
            code_type='email',
            expires_at=timezone.now() + timedelta(minutes=15)
        )
        
        # TODO: Send actual email
        # For now, just show in console
        print(f"Verification code for {self.object.email}: {code}")


class PasswordResetView(View):
    """Password reset request view"""
    template_name = 'auth/password_reset.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Generate reset code
            import random
            code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            
            VerificationCode.objects.create(
                user=user,
                code=code,
                code_type='password_reset',
                expires_at=timezone.now() + timedelta(minutes=15)
            )
            
            # TODO: Send email
            messages.success(request, 'Код відновлення відправлено на ваш email.')
        except User.DoesNotExist:
            messages.error(request, 'Користувача з таким email не знайдено.')
        
        return redirect('accounts:password_reset')


class VerifyEmailView(View):
    """Email verification view"""
    def get(self, request, code):
        try:
            verification = VerificationCode.objects.get(
                code=code,
                code_type='email',
                used_at__isnull=True
            )
            
            if verification.is_expired:
                messages.error(request, 'Код верифікації закінчився.')
            else:
                verification.user.is_email_verified = True
                verification.user.save()
                verification.used_at = timezone.now()
                verification.save()
                messages.success(request, 'Email успішно підтверджено!')
            
        except VerificationCode.DoesNotExist:
            messages.error(request, 'Невірний код верифікації.')
        
        return redirect('accounts:profile')


class VerifyPhoneView(View):
    """Phone verification view"""
    def get(self, request, code):
        try:
            verification = VerificationCode.objects.get(
                code=code,
                code_type='phone',
                used_at__isnull=True
            )
            
            if verification.is_expired:
                messages.error(request, 'Код верифікації закінчився.')
            else:
                verification.user.is_phone_verified = True
                verification.user.save()
                verification.used_at = timezone.now()
                verification.save()
                messages.success(request, 'Телефон успішно підтверджено!')
            
        except VerificationCode.DoesNotExist:
            messages.error(request, 'Невірний код верифікації.')
        
        return redirect('accounts:profile')


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile dashboard"""
    template_name = 'account/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user's active subscription
        context['active_subscription'] = user.subscriptions.filter(
            status='active',
            end_date__gte=timezone.now()
        ).first()
        
        # Get recent courses
        context['recent_courses'] = user.course_progress.select_related(
            'course'
        ).order_by('-last_accessed')[:5]
        
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Edit user profile"""
    model = Profile
    form_class = ProfileForm
    template_name = 'account/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user.profile
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Check if this is first time completing survey
        if not form.instance.completed_survey and all([
            form.cleaned_data.get('first_name'),
            form.cleaned_data.get('last_name'),
            form.cleaned_data.get('profession')
        ]):
            form.instance.completed_survey = True
            form.instance.survey_completed_at = timezone.now()
            form.instance.save()
            
            # TODO: Give survey bonus
            messages.success(self.request, 'Дякуємо за заповнення анкети! Ви отримали бонус.')
        
        messages.success(self.request, 'Профіль успішно оновлено.')
        return response


class SubscriptionView(LoginRequiredMixin, TemplateView):
    """User subscription management"""
    template_name = 'account/subscription.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Current subscription
        context['current_subscription'] = user.subscriptions.filter(
            status='active',
            end_date__gte=timezone.now()
        ).first()
        
        # Subscription history
        context['subscription_history'] = user.subscriptions.order_by('-created_at')[:10]
        
        # Available plans
        from apps.subscriptions.models import Plan
        context['available_plans'] = Plan.objects.filter(is_active=True).order_by('duration_months')
        
        # Ticket balance
        from apps.subscriptions.models import TicketBalance
        context['ticket_balance'] = TicketBalance.objects.filter(
            user=user,
            amount__gt=0,
            expires_at__gt=timezone.now()
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        return context


class MyCoursesView(LoginRequiredMixin, TemplateView):
    """User's courses and progress"""
    template_name = 'account/my_courses.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Course progress
        progress_queryset = user.course_progress.select_related('course').order_by('-last_accessed')
        
        # Filter by status
        status_filter = self.request.GET.get('status', 'all')
        if status_filter == 'completed':
            progress_queryset = progress_queryset.filter(completed_at__isnull=False)
        elif status_filter == 'in_progress':
            progress_queryset = progress_queryset.filter(
                completed_at__isnull=True,
                progress_percentage__gt=0
            )
        elif status_filter == 'not_started':
            progress_queryset = progress_queryset.filter(progress_percentage=0)
        
        context['course_progress'] = progress_queryset
        context['current_status'] = status_filter
        
        # Statistics
        context['stats'] = {
            'total_courses': user.course_progress.count(),
            'completed_courses': user.course_progress.filter(completed_at__isnull=False).count(),
            'in_progress_courses': user.course_progress.filter(
                completed_at__isnull=True,
                progress_percentage__gt=0
            ).count(),
        }
        
        # Recent favorites
        context['recent_favorites'] = user.favorites.select_related('course').order_by('-created_at')[:5]
        
        return context


class MyEventsView(LoginRequiredMixin, TemplateView):
    """User's event tickets and history"""
    template_name = 'account/my_events.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Event tickets
        tickets_queryset = user.event_tickets.select_related('event').order_by('-created_at')
        
        # Filter by status
        status_filter = self.request.GET.get('status', 'all')
        if status_filter == 'upcoming':
            tickets_queryset = tickets_queryset.filter(
                event__start_datetime__gte=timezone.now(),
                status__in=['confirmed', 'pending']
            )
        elif status_filter == 'past':
            tickets_queryset = tickets_queryset.filter(
                event__start_datetime__lt=timezone.now()
            )
        elif status_filter == 'used':
            tickets_queryset = tickets_queryset.filter(status='used')
        
        context['event_tickets'] = tickets_queryset
        context['current_status'] = status_filter
        
        # Separate upcoming and past
        all_tickets = user.event_tickets.select_related('event').order_by('-created_at')
        context['upcoming_events'] = [
            t for t in all_tickets 
            if t.event.start_datetime >= timezone.now() and t.status in ['confirmed', 'pending']
        ]
        context['past_events'] = [
            t for t in all_tickets 
            if t.event.start_datetime < timezone.now()
        ]
        
        # Statistics
        context['stats'] = {
            'total_events': all_tickets.count(),
            'upcoming_events': len(context['upcoming_events']),
            'attended_events': all_tickets.filter(status='used').count(),
        }
        
        return context


class SettingsView(LoginRequiredMixin, TemplateView):
    """User account settings"""
    template_name = 'account/settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # User forms
        from .forms import UserUpdateForm, PasswordChangeForm
        context['user_form'] = UserUpdateForm(instance=user, user=user)
        context['password_form'] = PasswordChangeForm(user=user)
        
        # Social accounts
        context['social_accounts'] = user.social_accounts.all()
        
        # Verification status
        context['verification_status'] = {
            'email_verified': user.is_email_verified,
            'phone_verified': user.is_phone_verified,
        }
        
        # Account statistics
        context['account_stats'] = {
            'member_since': user.created_at,
            'last_login': user.last_login,
            'total_orders': user.orders.count(),
            'total_payments': user.payments.filter(status='succeeded').count(),
        }
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle settings form submissions"""
        action = request.POST.get('action')
        
        if action == 'update_profile':
            return self.handle_profile_update(request)
        elif action == 'change_password':
            return self.handle_password_change(request)
        elif action == 'send_verification':
            return self.handle_send_verification(request)
        
        return redirect('accounts:settings')
    
    def handle_profile_update(self, request):
        """Handle profile update"""
        from .forms import UserUpdateForm
        form = UserUpdateForm(request.POST, instance=request.user, user=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Профіль оновлено')
        else:
            for error in form.errors.values():
                messages.error(request, error[0])
        
        return redirect('accounts:settings')
    
    def handle_password_change(self, request):
        """Handle password change"""
        from .forms import PasswordChangeForm
        form = PasswordChangeForm(request.user, request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Пароль змінено')
            # Update session to prevent logout
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
        else:
            for error in form.errors.values():
                messages.error(request, error[0])
        
        return redirect('accounts:settings')
    
    def handle_send_verification(self, request):
        """Handle verification code sending"""
        code_type = request.POST.get('code_type', 'email')
        
        if code_type == 'email' and request.user.is_email_verified:
            messages.warning(request, 'Email вже підтверджений')
            return redirect('accounts:settings')
        
        if code_type == 'phone' and request.user.is_phone_verified:
            messages.warning(request, 'Телефон вже підтверджений')
            return redirect('accounts:settings')
        
        # Generate and send verification code
        import random
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        VerificationCode.objects.create(
            user=request.user,
            code=code,
            code_type=code_type,
            expires_at=timezone.now() + timedelta(minutes=15)
        )
        
        # TODO: Send actual email/SMS
        messages.success(request, f'Код підтвердження відправлено на ваш {code_type}')
        
        return redirect('accounts:settings')


# Dashboard and additional cabinet views

class DashboardView(LoginRequiredMixin, TemplateView):
    """User dashboard - main cabinet page"""
    template_name = 'account/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Active subscription
        context['active_subscription'] = user.subscriptions.filter(
            status='active',
            end_date__gte=timezone.now()
        ).first()
        
        # Recent courses
        context['recent_courses'] = user.course_progress.select_related(
            'course'
        ).order_by('-last_accessed')[:5]
        
        # Upcoming events
        context['upcoming_events'] = user.event_tickets.filter(
            event__start_datetime__gte=timezone.now(),
            status__in=['confirmed', 'pending']
        ).select_related('event')[:3]
        
        # Quick stats
        context['stats'] = {
            'total_courses': user.course_progress.count(),
            'completed_courses': user.course_progress.filter(completed_at__isnull=False).count(),
            'upcoming_events': context['upcoming_events'].count(),
            'total_payments': user.payments.filter(status='succeeded').count(),
        }
        
        # Check if profile is complete
        profile = getattr(user, 'profile', None)
        context['profile_complete'] = (
            profile and 
            profile.first_name and 
            profile.last_name and 
            profile.completed_survey
        )
        
        context['under_development'] = True
        return context


class MyFilesView(LoginRequiredMixin, TemplateView):
    """User's accessible files and materials"""
    template_name = 'account/files.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get accessible courses through subscription or individual purchases
        accessible_courses = []
        
        # Through subscription
        active_subscription = user.subscriptions.filter(
            status='active',
            end_date__gte=timezone.now()
        ).first()
        
        if active_subscription:
            # TODO: Add subscription-based course access logic
            from apps.content.models import Course
            accessible_courses.extend(Course.objects.filter(requires_subscription=True))
        
        # Through individual purchases
        # TODO: Add individual purchase logic
        
        # Get progress for accessible courses
        progress_map = {
            p.course_id: p for p in user.course_progress.filter(
                course__in=accessible_courses
            ).select_related('course')
        }
        
        context['accessible_courses'] = accessible_courses
        context['progress_map'] = progress_map
        context['active_subscription'] = active_subscription
        
        # Favorites
        context['favorites'] = user.favorites.select_related('course').order_by('-created_at')
        
        # File statistics
        context['stats'] = {
            'total_accessible': len(accessible_courses),
            'in_progress': len([p for p in progress_map.values() if 0 < p.progress_percentage < 100]),
            'completed': len([p for p in progress_map.values() if p.progress_percentage == 100]),
            'favorites': context['favorites'].count(),
        }
        
        context['under_development'] = True
        return context


class PaymentHistoryView(LoginRequiredMixin, TemplateView):
    """User's payment history and orders"""
    template_name = 'account/payments.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Payment history
        payments = user.payments.order_by('-created_at')
        
        # Filter by status if requested
        status_filter = self.request.GET.get('status', 'all')
        if status_filter != 'all':
            payments = payments.filter(status=status_filter)
        
        # Filter by type if requested
        type_filter = self.request.GET.get('type', 'all')
        if type_filter != 'all':
            payments = payments.filter(payment_type=type_filter)
        
        context['payments'] = payments[:20]  # Last 20 payments
        context['current_status'] = status_filter
        context['current_type'] = type_filter
        
        # Payment statistics
        successful_payments = user.payments.filter(status='succeeded')
        context['stats'] = {
            'total_payments': user.payments.count(),
            'successful_payments': successful_payments.count(),
            'total_amount': successful_payments.aggregate(
                total=models.Sum('amount')
            )['total'] or 0,
            'last_payment_date': user.payments.filter(
                status='succeeded'
            ).order_by('-completed_at').first()
        }
        
        # Orders
        context['recent_orders'] = user.orders.order_by('-created_at')[:10]
        
        context['under_development'] = True
        return context


class LoyaltyView(LoginRequiredMixin, TemplateView):
    """User's loyalty program status"""
    template_name = 'account/loyalty.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get or create loyalty account
        loyalty_account, created = user.loyalty_accounts.get_or_create(
            defaults={'points': 0, 'tier': 'Bronze'}
        )
        
        context['loyalty_account'] = loyalty_account
        
        # Tier information
        tier_info = {
            'Bronze': {'min_points': 0, 'discount': 0, 'next_tier': 'Silver'},
            'Silver': {'min_points': 200, 'discount': 5, 'next_tier': 'Gold'},
            'Gold': {'min_points': 500, 'discount': 10, 'next_tier': 'Platinum'},
            'Platinum': {'min_points': 1000, 'discount': 15, 'next_tier': None},
        }
        
        current_tier_info = tier_info.get(loyalty_account.tier, tier_info['Bronze'])
        context['current_tier_info'] = current_tier_info
        
        # Progress to next tier
        if current_tier_info['next_tier']:
            next_tier_info = tier_info[current_tier_info['next_tier']]
            points_needed = next_tier_info['min_points'] - loyalty_account.points
            progress_percentage = min(
                (loyalty_account.points / next_tier_info['min_points']) * 100, 
                100
            )
            context['next_tier_info'] = next_tier_info
            context['points_needed'] = max(points_needed, 0)
            context['progress_percentage'] = progress_percentage
        
        # Recent point transactions
        context['recent_transactions'] = user.point_transactions.order_by('-created_at')[:10]
        
        # Available rewards/discounts
        context['available_discounts'] = [
            {
                'title': f'Знижка {current_tier_info["discount"]}%',
                'description': 'На всі товари та послуги',
                'active': True
            }
        ]
        
        context['under_development'] = True
        return context