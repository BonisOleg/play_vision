from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.utils import timezone
from datetime import timedelta
import random

from .models import User, Profile, VerificationCode
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    ProfileSerializer, ProfileUpdateSerializer, PasswordChangeSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    VerificationCodeSerializer, UserAccountSerializer
)


class CheckEmailView(APIView):
    """Check if email is already registered"""
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        email = request.data.get('email', '').lower()
        
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        exists = User.objects.filter(email=email).exists()
        
        return Response({
            'exists': exists,
            'message': 'Email вже зареєстрований' if exists else 'Email доступний'
        })


class VerifyCodeView(APIView):
    """Verify email/phone verification code"""
    
    def post(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        code = request.data.get('code')
        code_type = request.data.get('type', 'email')
        
        if not code:
            return Response(
                {'error': 'Code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            verification = VerificationCode.objects.get(
                user=request.user,
                code=code,
                code_type=code_type,
                used_at__isnull=True
            )
            
            if verification.is_expired:
                return Response(
                    {'error': 'Code has expired'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Mark code as used
            verification.used_at = timezone.now()
            verification.save()
            
            # Update user verification status
            if code_type == 'email':
                request.user.is_email_verified = True
                request.user.save()
                message = 'Email успішно підтверджено'
            elif code_type == 'phone':
                request.user.is_phone_verified = True
                request.user.save()
                message = 'Телефон успішно підтверджено'
            else:
                message = 'Код підтверджено'
            
            return Response({
                'success': True,
                'message': message
            })
            
        except VerificationCode.DoesNotExist:
            return Response(
                {'error': 'Invalid code'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserRegistrationAPIView(APIView):
    """User registration via API"""
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate email verification code
            self.send_verification_email(user)
            
            # Create token for immediate login
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'success': True,
                'message': 'Акаунт успішно створено',
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def send_verification_email(self, user):
        """Generate and send email verification code"""
        from .services import EmailService
        EmailService.send_email_verification_code(user)


class UserLoginAPIView(APIView):
    """User login via API"""
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        serializer = UserLoginSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Create or get token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'success': True,
                'message': 'Успішний вхід',
                'user': UserSerializer(user).data,
                'token': token.key
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutAPIView(APIView):
    """User logout via API"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            # Delete the user's token
            request.user.auth_token.delete()
            return Response({
                'success': True,
                'message': 'Успішний вихід'
            })
        except:
            return Response({
                'success': True,
                'message': 'Вихід виконано'
            })


class UserProfileAPIView(APIView):
    """Get/Update user profile"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserAccountSerializer(request.user)
        return Response(serializer.data)
    
    def patch(self, request):
        # Update user basic info
        user_data = {}
        if 'email' in request.data:
            user_data['email'] = request.data['email']
        if 'phone' in request.data:
            user_data['phone'] = request.data['phone']
        
        if user_data:
            user_serializer = UserSerializer(
                request.user,
                data=user_data,
                partial=True
            )
            if user_serializer.is_valid():
                user_serializer.save()
            else:
                return Response(
                    user_serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Update profile
        profile_serializer = ProfileUpdateSerializer(
            request.user.profile,
            data=request.data,
            partial=True
        )
        
        if profile_serializer.is_valid():
            profile_serializer.save()
            
            # Return updated user data
            user_serializer = UserAccountSerializer(request.user)
            return Response({
                'success': True,
                'message': 'Профіль оновлено',
                'user': user_serializer.data
            })
        
        return Response(
            profile_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class PasswordChangeAPIView(APIView):
    """Change user password"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            
            # Delete all tokens to force re-login
            Token.objects.filter(user=request.user).delete()
            
            return Response({
                'success': True,
                'message': 'Пароль успішно змінено. Увійдіть знову.'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestAPIView(APIView):
    """Request password reset"""
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            # Generate reset code
            code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            
            VerificationCode.objects.create(
                user=user,
                code=code,
                code_type='password_reset',
                expires_at=timezone.now() + timedelta(minutes=15)
            )
            
            # Send password reset email
            from django.core.mail import send_mail
            from django.conf import settings
            
            subject = 'Відновлення пароля - Play Vision'
            message = f'''
Вітаємо!

Ви запросили відновлення пароля для вашого акаунту Play Vision.

Ваш код відновлення: {code}

Код дійсний протягом 15 хвилин.

Якщо ви не запитували відновлення пароля, проігноруйте цей лист.

З повагою,
Команда Play Vision
            '''
            
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True,
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send password reset email: {e}")
            
            return Response({
                'success': True,
                'message': 'Код відновлення відправлено на ваш email'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmAPIView(APIView):
    """Confirm password reset with code"""
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Delete all tokens for this user
            Token.objects.filter(user=user).delete()
            
            return Response({
                'success': True,
                'message': 'Пароль успішно відновлено'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendVerificationCodeAPIView(APIView):
    """Send new verification code"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        code_type = request.data.get('type', 'email')
        
        if code_type not in ['email', 'phone']:
            return Response(
                {'error': 'Invalid code type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already verified
        if code_type == 'email' and request.user.is_email_verified:
            return Response(
                {'error': 'Email вже підтверджений'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if code_type == 'phone' and request.user.is_phone_verified:
            return Response(
                {'error': 'Телефон вже підтверджений'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate and send new code
        if code_type == 'email':
            from .services import EmailService
            success = EmailService.send_email_verification_code(request.user)
            message = 'Код підтвердження відправлено на ваш email'
        elif code_type == 'phone':
            # Phone verification not implemented yet
            code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            VerificationCode.objects.create(
                user=request.user,
                code=code,
                code_type=code_type,
                expires_at=timezone.now() + timedelta(minutes=15)
            )
            message = 'Код підтвердження відправлено на ваш телефон (SMS функціонал в розробці)'
        else:
            return Response(
                {'error': 'Невідомий тип коду'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'success': True,
            'message': message
        })


class VerifyCodeAPIView(APIView):
    """Verify email/phone code via API"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = VerificationCodeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            verification = serializer.validated_data['verification']
            code_type = serializer.validated_data['code_type']
            
            # Mark code as used
            verification.used_at = timezone.now()
            verification.save()
            
            # Update user verification status
            if code_type == 'email':
                request.user.is_email_verified = True
                message = 'Email успішно підтверджено'
            elif code_type == 'phone':
                request.user.is_phone_verified = True
                message = 'Телефон успішно підтверджено'
            
            request.user.save()
            
            return Response({
                'success': True,
                'message': message
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSubscriptionInfoAPIView(APIView):
    """Get user subscription information"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Current subscription
        current_subscription = user.subscriptions.filter(
            status='active',
            end_date__gte=timezone.now()
        ).first()
        
        # Subscription history
        subscription_history = user.subscriptions.order_by('-created_at')[:5]
        
        # Ticket balance (for Pro-Vision)
        # TODO: TicketBalance видалено - нова система підписок
# from apps.subscriptions.models import TicketBalance
        ticket_balance = TicketBalance.objects.filter(
            user=user,
            amount__gt=0,
            expires_at__gt=timezone.now()
        ).count()
        
        data = {
            'has_active_subscription': bool(current_subscription),
            'current_subscription': None,
            'ticket_balance': ticket_balance,
            'subscription_history': []
        }
        
        if current_subscription:
            data['current_subscription'] = {
                'id': current_subscription.id,
                'plan_name': current_subscription.plan.name,
                'plan_duration': current_subscription.plan.get_duration_display(),
                'start_date': current_subscription.start_date,
                'end_date': current_subscription.end_date,
                'days_remaining': current_subscription.days_remaining,
                'auto_renew': current_subscription.auto_renew,
                'status': current_subscription.status
            }
        
        for sub in subscription_history:
            data['subscription_history'].append({
                'plan_name': sub.plan.name,
                'start_date': sub.start_date,
                'end_date': sub.end_date,
                'status': sub.status
            })
        
        return Response(data)


class UserCoursesAPIView(APIView):
    """Get user's course progress and access"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # User's course progress
        progress_data = user.course_progress.select_related('course').order_by('-last_accessed')
        
        courses = []
        for progress in progress_data:
            courses.append({
                'course': {
                    'id': progress.course.id,
                    'title': progress.course.title,
                    'slug': progress.course.slug,
                    'thumbnail': progress.course.thumbnail.url if progress.course.thumbnail else None,
                    'category': progress.course.category.name,
                    'difficulty': progress.course.get_difficulty_display(),
                    'duration_display': progress.course.duration_display
                },
                'progress': {
                    'percentage': float(progress.progress_percentage),
                    'started_at': progress.started_at,
                    'last_accessed': progress.last_accessed,
                    'completed_at': progress.completed_at,
                    'is_completed': bool(progress.completed_at)
                }
            })
        
        # Statistics
        stats = {
            'total_courses': progress_data.count(),
            'completed_courses': progress_data.filter(completed_at__isnull=False).count(),
            'in_progress_courses': progress_data.filter(
                completed_at__isnull=True,
                progress_percentage__gt=0
            ).count(),
            'total_watch_time': 0  # TODO: Implement watch time tracking
        }
        
        return Response({
            'courses': courses,
            'statistics': stats
        })


class UserEventsAPIView(APIView):
    """Get user's event tickets and registrations"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # User's event tickets
        tickets = user.event_tickets.select_related('event').order_by('-created_at')
        
        events = []
        for ticket in tickets:
            events.append({
                'ticket': {
                    'id': ticket.id,
                    'ticket_number': ticket.ticket_number,
                    'status': ticket.status,
                    'used_balance': ticket.used_balance,
                    'qr_code': ticket.qr_code.url if ticket.qr_code else None,
                    'created_at': ticket.created_at,
                    'used_at': ticket.used_at
                },
                'event': {
                    'id': ticket.event.id,
                    'title': ticket.event.title,
                    'slug': ticket.event.slug,
                    'event_type': ticket.event.get_event_type_display(),
                    'start_datetime': ticket.event.start_datetime,
                    'end_datetime': ticket.event.end_datetime,
                    'location': ticket.event.location,
                    'is_online': ticket.event.is_online,
                    'thumbnail': ticket.event.thumbnail.url if ticket.event.thumbnail else None
                }
            })
        
        # Separate upcoming and past events
        upcoming_events = [e for e in events if e['event']['start_datetime'] > timezone.now()]
        past_events = [e for e in events if e['event']['start_datetime'] <= timezone.now()]
        
        return Response({
            'upcoming_events': upcoming_events,
            'past_events': past_events,
            'total_events': len(events)
        })


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_user_account(request):
    """Delete user account"""
    user = request.user
    
    # TODO: Add additional confirmation logic
    # For now, just mark as inactive
    user.is_active = False
    user.save()
    
    # Delete tokens
    Token.objects.filter(user=user).delete()
    
    return Response({
        'success': True,
        'message': 'Акаунт деактивовано'
    })
