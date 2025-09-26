from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User, Profile


class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form"""
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    phone = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-input--phone',
            'placeholder': 'XX XXX XX XX',
            'pattern': '[0-9]{9}',
            'maxlength': '9'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Підтвердіть пароль'
        })
    )
    agree_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Я погоджуюся з умовами використання та політикою приватності'
    )
    
    class Meta:
        model = User
        fields = ('email', 'phone', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove username field
        if 'username' in self.fields:
            del self.fields['username']
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        phone = cleaned_data.get('phone')
        agree_terms = cleaned_data.get('agree_terms')
        
        # Check if user agreed to terms
        if not agree_terms:
            raise ValidationError('Необхідно погодитися з умовами використання')
        
        # Require either email or phone
        if not email and not phone:
            raise ValidationError('Вкажіть email або номер телефону')
        
        # Format phone number
        if phone:
            phone = '+380' + phone.strip()
            cleaned_data['phone'] = phone
        
        return cleaned_data
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError('Користувач з таким email вже існує')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Format phone number
            if not phone.startswith('+380'):
                phone = '+380' + phone.strip()
            
            # Check if phone already exists
            if User.objects.filter(phone=phone).exists():
                raise ValidationError('Користувач з таким номером телефону вже існує')
        return phone
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Set phone_registered_at if registering with phone only
        if user.phone and not user.email:
            from django.utils import timezone
            user.phone_registered_at = timezone.now()
        
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    """User profile form"""
    
    class Meta:
        model = Profile
        fields = [
            'first_name', 'last_name', 'birth_date', 'avatar',
            'profession', 'interests'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ім\'я'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Прізвище'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'profession': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Професія'
            }),
            'interests': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields not required for partial updates
        for field_name, field in self.fields.items():
            field.required = False


class UserUpdateForm(forms.ModelForm):
    """User basic info update form"""
    
    class Meta:
        model = User
        fields = ['email', 'phone']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+380xxxxxxxxx'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and self.user:
            # Check if email is already taken by another user
            if User.objects.filter(email=email).exclude(id=self.user.id).exists():
                raise ValidationError('Цей email вже використовується')
        return email


class PasswordChangeForm(forms.Form):
    """Password change form"""
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поточний пароль'
        })
    )
    new_password1 = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Новий пароль'
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Підтвердіть новий пароль'
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise ValidationError('Неправильний поточний пароль')
        return old_password
    
    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise ValidationError('Нові паролі не співпадають')
        
        return cleaned_data
    
    def save(self):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        self.user.save()
        return self.user


class PasswordResetForm(forms.Form):
    """Password reset request form"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError('Користувача з таким email не знайдено')
        return email


class PasswordResetConfirmForm(forms.Form):
    """Password reset confirmation form"""
    code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Код з email'
        })
    )
    new_password1 = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Новий пароль'
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Підтвердіть новий пароль'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise ValidationError('Паролі не співпадають')
        
        return cleaned_data


class VerificationCodeForm(forms.Form):
    """Email/Phone verification form"""
    code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Код підтвердження'
        })
    )


class AddEmailForm(forms.Form):
    """Form to add email to phone-only accounts"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введіть ваш email'
        }),
        help_text='Ми відправимо код підтвердження на цю адресу'
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email is already taken by another user
            if User.objects.filter(email=email).exclude(id=self.user.id if self.user else None).exists():
                raise ValidationError('Цей email вже використовується іншим користувачем')
        return email


class DeleteAccountForm(forms.Form):
    """Account deletion confirmation form"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Підтвердіть паролем'
        })
    )
    confirm_deletion = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Я розумію, що це дія незворотна'
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise ValidationError('Неправильний пароль')
        return password