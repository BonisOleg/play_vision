from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import User, Profile, SocialAccount, VerificationCode


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user serializer for references"""
    full_name = serializers.CharField(source='profile.full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'created_at']


class ProfileSerializer(serializers.ModelSerializer):
    """User profile serializer"""
    avatar_url = serializers.CharField(source='get_avatar_url', read_only=True)
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'first_name', 'last_name', 'full_name', 'birth_date',
            'avatar', 'avatar_url', 'profession', 'interests',
            'completed_survey', 'survey_completed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['completed_survey', 'survey_completed_at', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """Detailed user serializer"""
    profile = ProfileSerializer(read_only=True)
    has_active_subscription = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone', 'is_email_verified', 'is_phone_verified',
            'profile', 'has_active_subscription', 'created_at'
        ]
        read_only_fields = ['id', 'is_email_verified', 'is_phone_verified', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Паролі не співпадають")
        
        # Remove password_confirm as it's not needed for user creation
        attrs.pop('password_confirm')
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        
        # Create profile
        Profile.objects.create(user=user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """User login serializer"""
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError('Невірний email або пароль')
            
            if not user.is_active:
                raise serializers.ValidationError('Акаунт деактивований')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Email та пароль обов\'язкові')


class PasswordChangeSerializer(serializers.Serializer):
    """Password change serializer"""
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    new_password_confirm = serializers.CharField()
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Неправильний поточний пароль')
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError('Нові паролі не співпадають')
        return attrs
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """Password reset request serializer"""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Користувача з таким email не існує')
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Password reset confirm serializer"""
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8)
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError('Паролі не співпадають')
        
        # Validate reset code
        try:
            user = User.objects.get(email=attrs['email'])
            verification = VerificationCode.objects.get(
                user=user,
                code=attrs['code'],
                code_type='password_reset',
                used_at__isnull=True
            )
            
            if verification.is_expired:
                raise serializers.ValidationError('Код відновлення закінчився')
            
            attrs['user'] = user
            attrs['verification'] = verification
            
        except (User.DoesNotExist, VerificationCode.DoesNotExist):
            raise serializers.ValidationError('Невірний код відновлення')
        
        return attrs
    
    def save(self):
        user = self.validated_data['user']
        verification = self.validated_data['verification']
        
        # Update password
        user.set_password(self.validated_data['new_password'])
        user.save()
        
        # Mark verification code as used
        verification.used_at = timezone.now()
        verification.save()
        
        return user


class VerificationCodeSerializer(serializers.Serializer):
    """Verification code serializer"""
    code = serializers.CharField(max_length=6)
    code_type = serializers.ChoiceField(choices=['email', 'phone'])
    
    def validate(self, attrs):
        user = self.context['request'].user
        
        try:
            verification = VerificationCode.objects.get(
                user=user,
                code=attrs['code'],
                code_type=attrs['code_type'],
                used_at__isnull=True
            )
            
            if verification.is_expired:
                raise serializers.ValidationError('Код верифікації закінчився')
            
            attrs['verification'] = verification
            
        except VerificationCode.DoesNotExist:
            raise serializers.ValidationError('Невірний код верифікації')
        
        return attrs


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Profile update serializer"""
    
    class Meta:
        model = Profile
        fields = [
            'first_name', 'last_name', 'birth_date', 'avatar',
            'profession', 'interests'
        ]
    
    def update(self, instance, validated_data):
        # Check if survey is being completed for the first time
        completing_survey = (
            not instance.completed_survey and
            validated_data.get('first_name') and
            validated_data.get('last_name') and
            validated_data.get('profession')
        )
        
        instance = super().update(instance, validated_data)
        
        if completing_survey:
            instance.completed_survey = True
            instance.survey_completed_at = timezone.now()
            instance.save()
        
        return instance


class SocialAccountSerializer(serializers.ModelSerializer):
    """Social account serializer"""
    
    class Meta:
        model = SocialAccount
        fields = ['provider', 'provider_id', 'extra_data', 'created_at']
        read_only_fields = ['created_at']


class UserAccountSerializer(serializers.ModelSerializer):
    """Full user account data serializer"""
    profile = ProfileSerializer(read_only=True)
    social_accounts = SocialAccountSerializer(many=True, read_only=True)
    has_active_subscription = serializers.BooleanField(read_only=True)
    
    # Subscription info
    current_subscription = serializers.SerializerMethodField()
    
    # Statistics
    completed_courses_count = serializers.SerializerMethodField()
    total_watch_time = serializers.SerializerMethodField()
    upcoming_events_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone', 'is_email_verified', 'is_phone_verified',
            'profile', 'social_accounts', 'has_active_subscription',
            'current_subscription', 'completed_courses_count',
            'total_watch_time', 'upcoming_events_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_current_subscription(self, obj):
        subscription = obj.subscriptions.filter(
            status='active',
            end_date__gte=timezone.now()
        ).first()
        
        if subscription:
            return {
                'plan_name': subscription.plan.name,
                'end_date': subscription.end_date,
                'days_remaining': subscription.days_remaining,
                'auto_renew': subscription.auto_renew
            }
        return None
    
    def get_completed_courses_count(self, obj):
        return obj.course_progress.filter(
            completed_at__isnull=False
        ).count()
    
    def get_total_watch_time(self, obj):
        # TODO: Implement watch time tracking
        return 0
    
    def get_upcoming_events_count(self, obj):
        return obj.event_tickets.filter(
            event__start_datetime__gte=timezone.now(),
            status='confirmed'
        ).count()
