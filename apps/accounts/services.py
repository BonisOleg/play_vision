"""
Email services for accounts app
"""
import random
from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from .models import VerificationCode


class EmailService:
    """Service for sending email verification codes"""
    
    @staticmethod
    def generate_verification_code():
        """Generate 6-digit verification code"""
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    @staticmethod
    def send_email_verification_code(user):
        """Send email verification code to user"""
        code = EmailService.generate_verification_code()
        
        # Create verification code record
        VerificationCode.objects.create(
            user=user,
            code=code,
            code_type='email',
            expires_at=timezone.now() + timedelta(minutes=15)
        )
        
        # Send email
        subject = 'Підтвердіть ваш email - Play Vision'
        message = f"""
Вітаємо у Play Vision!

Ваш код підтвердження: {code}

Код дійсний протягом 15 хвилин.

Якщо ви не реєструвались на нашому сайті, проігноруйте цей лист.

З повагою,
Команда Play Vision
        """
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            # Log error but don't break the flow
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send verification email to {user.email}: {e}")
            return False
    
    @staticmethod
    def send_email_reminder(user):
        """Send reminder to add and verify email"""
        days_left = 3 - user.days_since_phone_registration
        
        subject = 'Додайте email до вашого акаунту - Play Vision'
        message = f"""
Вітаємо!

Ви зареєструвались у Play Vision через номер телефону. 

Щоб не втратити доступ до акаунту, будь ласка, додайте email адресу 
в особистому кабінеті та підтвердіть її.

Залишилось днів: {days_left}

Увійти в кабінет: https://playvision.com/account/

З повагою,
Команда Play Vision
        """
        
        # Only send if user has email
        if not user.email:
            return False
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send reminder email to {user.email}: {e}")
            return False
