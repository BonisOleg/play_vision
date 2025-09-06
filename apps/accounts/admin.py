from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Profile, SocialAccount, VerificationCode


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'phone', 'is_email_verified', 'is_phone_verified', 
                   'is_staff', 'is_active', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_email_verified', 
                  'is_phone_verified', 'created_at')
    search_fields = ('email', 'phone', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone')}),
        (_('Verification'), {'fields': ('is_email_verified', 'is_phone_verified')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'created_at', 'updated_at')}),
        (_('Stripe'), {'fields': ('stripe_customer_id',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'profession', 'completed_survey', 'created_at')
    list_filter = ('completed_survey', 'created_at')
    search_fields = ('user__email', 'first_name', 'last_name', 'profession')
    raw_id_fields = ('user',)
    filter_horizontal = ('interests',)
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'birth_date', 'avatar', 'profession')
        }),
        ('Interests', {'fields': ('interests',)}),
        ('Survey', {'fields': ('completed_survey', 'survey_completed_at')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'survey_completed_at')


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'provider_id', 'created_at')
    list_filter = ('provider', 'created_at')
    search_fields = ('user__email', 'provider_id')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'code_type', 'is_expired', 'is_used', 'created_at')
    list_filter = ('code_type', 'created_at')
    search_fields = ('user__email', 'code')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at',)
    
    def is_used(self, obj):
        return obj.is_used
    is_used.boolean = True
    is_used.short_description = 'Used'