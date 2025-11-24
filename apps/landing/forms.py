from django import forms
from django.core.validators import RegexValidator
import re


class LeadForm(forms.Form):
    """Форма для збору заявок на landing page"""
    
    # Валідатор для українських номерів
    phone_regex = RegexValidator(
        regex=r'^\+380\d{9}$',
        message='Введіть коректний український номер у форматі +380XXXXXXXXX'
    )
    
    # Валідатор для імені (лише літери та пробіли)
    name_regex = RegexValidator(
        regex=r'^[a-zA-Zа-яА-ЯіІїЇєЄґҐ\s\'\-]+$',
        message='Ім\'я може містити лише літери, пробіли, апострофи та дефіси'
    )
    
    full_name = forms.CharField(
        label='Ваше ім\'я та прізвище',
        max_length=255,
        required=True,
        validators=[name_regex],
        widget=forms.TextInput(attrs={
            'placeholder': 'Ваше ім\'я та прізвище',
            'class': 'landing-input',
            'autocomplete': 'name',
        }),
        error_messages={
            'required': 'Будь ласка, вкажіть ваше ім\'я та прізвище',
            'max_length': 'Ім\'я занадто довге (максимум 255 символів)',
        }
    )
    
    phone = forms.CharField(
        label='Ваш мобільний',
        max_length=20,
        required=True,
        validators=[phone_regex],
        widget=forms.TextInput(attrs={
            'placeholder': '+380(__) ___-__-__',
            'class': 'landing-input',
            'autocomplete': 'tel',
            'type': 'tel',
            'data-phone-input': 'true',
        }),
        error_messages={
            'required': 'Будь ласка, вкажіть ваш номер телефону',
        }
    )
    
    email = forms.EmailField(
        label='Ваш email',
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'ivan@example.com',
            'class': 'landing-input',
            'autocomplete': 'email',
        }),
        error_messages={
            'required': 'Будь ласка, вкажіть вашу електронну адресу',
            'invalid': 'Введіть коректну email адресу',
        }
    )
    
    def clean_phone(self):
        """Очистка та валідація номера телефону"""
        phone = self.cleaned_data.get('phone', '')
        
        # Видалити всі символи крім цифр та +
        phone = re.sub(r'[^\d+]', '', phone)
        
        # Переконатися що номер починається з +380
        if not phone.startswith('+380'):
            if phone.startswith('380'):
                phone = '+' + phone
            elif phone.startswith('0'):
                phone = '+38' + phone
            else:
                raise forms.ValidationError(
                    'Номер має починатися з +380 (український номер)'
                )
        
        # Перевірити довжину (+380 + 9 цифр = 13)
        if len(phone) != 13:
            raise forms.ValidationError(
                'Введіть повний номер телефону (10 цифр після +380)'
            )
        
        return phone
    
    def clean_full_name(self):
        """Очистка та валідація імені"""
        full_name = self.cleaned_data.get('full_name', '').strip()
        
        if len(full_name) < 2:
            raise forms.ValidationError(
                'Введіть ваше ім\'я та прізвище'
            )
        
        # Перевірити що є хоча б 2 слова (ім'я та прізвище)
        words = full_name.split()
        if len(words) < 2:
            raise forms.ValidationError(
                'Введіть ваше ім\'я та прізвище'
            )
        
        return full_name
    
    def clean_email(self):
        """Очистка email"""
        email = self.cleaned_data.get('email', '').strip().lower()
        return email

