from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.contrib.auth.validators import UnicodeUsernameValidator


class User(AbstractUser):
    """
    Custom User model for Play Vision
    """
    username_validator = UnicodeUsernameValidator()
    
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=[username_validator],
        error_messages={
            'unique': "A user with that username already exists.",
        },
        blank=True,
        null=True
    )
    email = models.EmailField('email address', unique=True, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, unique=True, null=True, help_text='Phone number in international format')
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    phone_registered_at = models.DateTimeField(null=True, blank=True, help_text='Date when user registered with phone only')
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Username не обов'язковий, оскільки може бути null
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email or self.phone or f"User {self.id}"
    
    def save(self, *args, **kwargs):
        # Convert empty strings to None for unique fields
        if self.email == '':
            self.email = None
        if self.phone == '':
            self.phone = None
        
        # Ensure we have either email or phone
        if not self.email and not self.phone:
            raise ValueError("User must have either email or phone")
        
        # Set username to email or phone
        if self.email:
            self.username = self.email
        elif self.phone:
            self.username = self.phone
        
        super().save(*args, **kwargs)
    
    @property
    def days_since_phone_registration(self):
        """Get days since phone-only registration"""
        if not self.phone_registered_at:
            return 0
        return (timezone.now() - self.phone_registered_at).days
    
    @property
    def phone_registration_expired(self):
        """Check if 3-day phone registration period has expired"""
        return self.phone_registered_at and self.days_since_phone_registration >= 3
    
    @property
    def needs_email_verification(self):
        """Check if user needs to add and verify email"""
        return bool(self.phone_registered_at and not self.is_email_verified)
    
    def has_active_subscription(self):
        """Check if user has active subscription"""
        return self.subscriptions.filter(
            status='active',
            end_date__gt=timezone.now()
        ).exists()
    
    def has_course_access(self, course):
        """Check if user has access to specific course"""
        from apps.content.utils import check_user_course_access
        return check_user_course_access(self, course)


class Profile(models.Model):
    """
    Extended user profile
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, max_length=500)
    profession = models.CharField(max_length=100, blank=True)
    completed_survey = models.BooleanField(default=False)
    survey_completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.email} profile"
    
    @property
    def full_name(self):
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.user.email
    
    def get_avatar_url(self):
        """Get avatar URL or default"""
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.png'


class SocialAccount(models.Model):
    """
    Social account connections
    """
    PROVIDER_CHOICES = [
        ('google', 'Google'),
        ('telegram', 'Telegram'),
        ('tiktok', 'TikTok'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_accounts')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    provider_id = models.CharField(max_length=100)
    extra_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'social_accounts'
        unique_together = ['provider', 'provider_id']
        verbose_name = 'Social Account'
        verbose_name_plural = 'Social Accounts'
    
    def __str__(self):
        return f"{self.user.email} - {self.provider}"


class VerificationCode(models.Model):
    """
    Email/Phone verification codes
    """
    CODE_TYPES = [
        ('email', 'Email Verification'),
        ('phone', 'Phone Verification'),
        ('password_reset', 'Password Reset'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_codes')
    code = models.CharField(max_length=6)
    code_type = models.CharField(max_length=20, choices=CODE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'verification_codes'
        verbose_name = 'Verification Code'
        verbose_name_plural = 'Verification Codes'
        indexes = [
            models.Index(fields=['user', 'code_type', 'code']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.code_type}"
    
    @property
    def is_expired(self):
        """Check if code is expired"""
        return timezone.now() > self.expires_at
    
    @property
    def is_used(self):
        """Check if code is used"""
        return self.used_at is not None
    
    def is_valid(self):
        """Check if code is valid"""
        return not self.is_expired and not self.is_used