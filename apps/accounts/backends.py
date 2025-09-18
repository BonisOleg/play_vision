from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to login with email, phone or username
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to find user by email, phone or username
            user = User.objects.get(
                Q(email=username) | Q(phone=username) | Q(username=username)
            )
        except User.DoesNotExist:
            return None
        
        # Check if phone registration expired (only for phone-only users)
        if user.phone_registered_at and user.phone_registration_expired and not user.is_email_verified:
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
